from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
import data_classes
import xml_helpers
import re
import csv


ns = {
    'h': 'http://www.eki.ee/dict/har',
    'xml': 'http://www.w3.org/XML/1998/namespace'
}

# Function to parse XML and create Concept objects
def parse_xml(dataset_code, file_path, sources_file_path):

    guid_word_dict = xml_helpers.build_guid_word_dict(file_path)

    sources_with_ids = xml_helpers.load_sources(sources_file_path)

    tree = ET.parse(file_path)
    root = tree.getroot()

    concepts = []
    sources = []

    all_relations = []

    for a_element in root.findall('.//h:A', ns):
        domains = []
        conceptids = []
        manualEventOn = None
        manualEventBy = None
        firstCreateEventOn = None
        firstCreateEventBy = None
        notes = []
        forums = []
        definitions = []
        words = []

        # Valdkonnad
        for v_element in a_element.findall('.//h:v', ns):
            d_domain = v_element.text
            d_origin = 'har'
            domain = {
                'code': d_domain,
                'origin': d_origin
            }
            domains.append(domain)

        # GUID
        for guid in a_element.findall('.//h:G', ns):
            conceptids.append(guid.text)

        # Koostamisaeg - createdAt
        for created_at in a_element.findall('.//h:KA', ns):
            firstCreateEventOn = created_at.text
            date_part = firstCreateEventOn.split("T")[0]
            parts = date_part.split("-")
            firstCreateEventOn = f"{parts[2]}.{parts[1]}.{parts[0]}"

        # Koostaja - creator
        for creator in a_element.findall('.//h:K', ns):
            firstCreateEventBy = creator.text

        # Viimane muutja
        for editor in a_element.findall('.//h:T', ns):
            manualEventBy = editor.text

        for tg_element in a_element.findall('.//h:tg', ns):
            definition, notes_from_xml, forums_from_xml, sources_from_xml, seotud_relations = tg_def_definition(tg_element, sources_with_ids, conceptids, guid_word_dict)

            if definition:
                definitions.append(definition)
            for note in notes_from_xml:
                if note.value:
                    notes.append(note)
            for forum in forums_from_xml:
                if forum.value:
                    forums.append(forum)
            for s in sources_from_xml:
                sources.append(s)

            if len(seotud_relations) > 0:
                for sr in seotud_relations:
                    all_relations.append(sr)

        # Kommentaarid

        for kom_group_element in a_element.findall('.//h:komg', ns):
            for kom_elem in kom_group_element.findall('.//h:kom', ns):
                content = kom_elem.text
            for kom_aut_elem in kom_group_element.findall('.//h:kaut', ns):
                author = kom_aut_elem.text
            for kom_t_elem in kom_group_element.findall('.//h:kaeg', ns):
                time = kom_t_elem.text

            notes.append(
                data_classes.Note(
                    value=content + ' (' + author + ', ' + time + ')',
                    lang='est',
                    publicity=False,
                    sourceLinks=[]
                )
            )

        words_from_est_terms, concept_notes = ter_word(sources_with_ids, a_element)

        # Eestikeelsed terminid
        for w in words_from_est_terms:
            words.append(w)

        for c in concept_notes:
            notes.append(c)

        # Võõrkeelsed vasted

        foreign_words, foreign_definitions, sources_from_xp = xp_to_words(a_element, sources_with_ids)

        for w in foreign_words:
            if w.valuePrese:
                words.append(w)

        for d in foreign_definitions:
            if d.value:
                definitions.append(d)

        for s in sources_from_xp:
            sources.append(s)

        # Koosta mõiste objekt
        concept = data_classes.Concept(
            datasetCode=dataset_code,
            conceptIds=conceptids,
            domains=domains,
            manualEventOn=manualEventOn,
            manualEventBy=manualEventBy,
            firstCreateEventOn=firstCreateEventOn,
            firstCreateEventBy=firstCreateEventBy,
            definitions=definitions,
            notes=notes,
            forums=forums,
            words=words
        )
        concepts.append(concept)

    with open('seosed.txt', 'w') as file:
        for item in all_relations:
            file.write(str(item) + '\n')

    return concepts


# Mõiste tähendusgrupp: tg : def - Definitsiooniks jmt
def tg_def_definition(tg_element, sources_with_ids, conceptids, guid_word_dict):
    def_value = None
    definition = None
    notes = []
    sourcelinks = []
    forums = []

    sources = []

    for dg_element in tg_element.findall('./h:dg', ns):
        for def_element in dg_element.findall('./h:def', ns):
            def_value = def_element.text
        for all_element in dg_element.findall('./h:all', ns):
            source_value = all_element.text
            sources.append(source_value)
            sourcelink = data_classes.Sourcelink(
                sourceId=xml_helpers.get_source_id_by_source_text(sources_with_ids, source_value),
                value=source_value,
                name='')
            sourcelinks.append(sourcelink)
        for dn_element in dg_element.findall('./h:dn', ns):
            if def_value:
                def_value = def_value + ', nt ' + dn_element.text
            else:
                notes.append(data_classes.Note(
                    value=dn_element.text,
                    lang='est',
                    publicity=True,
                    sourceLinks=[]
                ))

    for co_element in tg_element.findall('./h:co', ns):
        notes.append(data_classes.Note(
            value=co_element.text,
            lang='est',
            publicity=True,
            sourceLinks=[]
        ))

    meaning_relations = []


    # Tesaurus
    # Tähenduse seosed (ant > antonüüm)
    for tes_element in tg_element.findall('./h:tes', ns):
        for child in tes_element:
            tag_name = child.tag.split('}')[-1]

            if tag_name == 'ant':
                if xml_helpers.find_guid_by_term(child.text, guid_word_dict):
                    meaning_relations.append(str(conceptids[0]) + '; antonüüm; ' + xml_helpers.find_guid_by_term(child.text, guid_word_dict))
                elif child.text:
                    print('Vigane antonüüm: ' + child.text)
                else:
                    print('Puudub antonüüm: ' + str(conceptids[0]))
            else:
                print('Muud tüüpi: ' + str(conceptids[0]))

    # Tähenduse seose viited (vrd, vt ka > seotud)
    for evt_element in tg_element.findall('./h:evt', ns):
        evt_value = evt_element.text if evt_element.text is not None else ""
        evt_attrib_value = evt_element.attrib.get(f'{{{ns["h"]}}}evtl', '')

        if evt_attrib_value == "vrd":
            if evt_value:
                if xml_helpers.find_guid_by_term(evt_value, guid_word_dict):
                    relation = str(conceptids[0]) + '; seotud; ' + xml_helpers.find_guid_by_term(evt_value, guid_word_dict)
                    meaning_relations.append(relation)
                else:
                    print('Vigane viide: ' + evt_value)
        elif evt_attrib_value == "vt ka":
            if evt_value:
                if xml_helpers.find_guid_by_term(evt_value, guid_word_dict):
                    relation = str(conceptids[0]) + '; seotud; ' + xml_helpers.find_guid_by_term(evt_value, guid_word_dict)
                    meaning_relations.append(relation)
                else:
                    print('Vigane viide: ' + evt_value)
        else:
            continue

    if def_value:
        definition = data_classes.Definition(
            value=def_value,
            lang='est',
            definitionTypeCode='definitsioon',
            sourceLinks=sourcelinks)

    # Sisemärkus
    forum = None
    for mrk_element in tg_element.findall('./h:mrk', ns):
        mrk_maut_value = mrk_element.attrib.get(f'{{{ns["h"]}}}maut', '')
        mrk_maeg_value = mrk_element.attrib.get(f'{{{ns["h"]}}}maeg', '')
        forum_value = mrk_element.text
        if forum_value.startswith('['):
            sources.append(forum_value)
            name = xml_helpers.get_source_name_from_source(forum_value)
        elif forum_value.startswith('DEF: '):
            search_value = forum_value.replace('DEF: ', '').strip().strip('[').strip(']')
            definition.sourceLinks.append(data_classes.Sourcelink(
                sourceId=xml_helpers.get_source_id_by_source_text(sources_with_ids, search_value),
                value=search_value,
                name=''
            ))
            continue
        forum = data_classes.Forum(
            value=forum_value + ' (' + mrk_maut_value + ', ' + mrk_maeg_value + ')'
        )

    if forum is not None:
        forums.append(forum)

    return definition, notes, forums, sources, meaning_relations


# Vastete plokk
def xp_to_words(a_element, sources_with_ids):
    words = []
    sourcelinks = []
    wordtypecodes = []
    valuestatecode = None
    lexemevalue = None
    definitions = []

    sources_from_xp = []

    for xp_element in a_element.findall('.//h:xp', ns):
        lang = xp_element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', 'unknown')
        # Vaste keel

        for xg_element in xp_element.findall('./h:xg', ns):
            lexemenotes = []
            word_sourcelinks = []

            # Vaste
            for x_element in xg_element.findall('./h:x', ns):
                lexemevalue = x_element.text

                # Vaste liik
                liik = x_element.attrib.get(f'{{{ns["h"]}}}liik', '')
                if liik:
                    if liik == 'l':
                        wordtypecodes.append(liik)

                # Vaste tüüp
                tyyp = x_element.attrib.get(f'{{{ns["h"]}}}tyyp', '')
                if tyyp:
                    if tyyp == 'ee':
                        valuestatecode = 'eelistatud'
                    else:
                        valuestatecode = None

            # Kaudtõlge
            for xqd_element in xg_element.findall('./h:xqd', ns):
                def_value = xqd_element.text

                definitions.append(data_classes.Definition(
                    value=def_value,
                    lang=xml_helpers.map_lang_codes(lang),
                    definitionTypeCode='definitsioon',
                    sourceLinks=[]
                ))

            # Stiil
            for s_element in xg_element.findall('./h:s', ns):
                if s_element.text:
                    if s_element.text == 'halb':
                        valuestatecode = 'väldi'
                    elif s_element.text == 'van':
                        valuestatecode = 'vananenud'
                    elif s_element.text == 'kõnek':
                        break
                    elif s_element.text == 'aj':
                        break
                    else:
                        break

                    lexemenotes.append(data_classes.Lexemenote(
                        value='Stiil: ' + s_element.text,
                        lang=xml_helpers.map_lang_codes(lang),
                        publicity=True,
                        sourceLinks=sourcelinks
                    ))

            # Märkus
            for co_element in xg_element.findall('./h:co', ns):
                co_lang = co_element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', 'unknown')

                if co_element.text:
                    if '[EKSPERT]' in co_element.text:
                        lexemenotes.append(data_classes.Lexemenote(
                            value=co_element.text.replace(' [EKSPERT]', ''),
                            lang=xml_helpers.map_lang_codes(co_lang),
                            publicity=True,
                            sourceLinks=[data_classes.Sourcelink(
                                sourceId=xml_helpers.get_source_id_by_name('Ekspert'),
                                value='Ekspert',
                                name=''
                            )]
                        ))
                    else:
                        lexemenotes.append(data_classes.Lexemenote(
                            value=co_element.text,
                            lang=xml_helpers.map_lang_codes(co_lang),
                            publicity=True,
                            sourceLinks=[]
                        ))

            # Sisemärkus (mitteavalik ilmiku märkus)
            for mrk_element in xg_element.findall('./h:mrk', ns):
                mrk_lang_value = mrk_element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', 'unknown')
                mrk_maut_value = mrk_element.attrib.get(f'{{{ns["h"]}}}maut', '')
                mrk_maeg_value = mrk_element.attrib.get(f'{{{ns["h"]}}}maeg', '')

                mrk_value = mrk_element.text

                if mrk_value.startswith('['):
                    #print(mrk_value)
                    sources_from_xp.append(mrk_value)
                    continue

                lexemenotes.append(data_classes.Lexemenote(
                    value=mrk_value + ' (' + mrk_maut_value + ', ' + mrk_maeg_value + ')',
                    lang=xml_helpers.map_lang_codes(mrk_lang_value),
                    publicity=False,
                    sourceLinks=[]
                ))

            # Grammatika grupp
            for xgrg_element in xg_element.findall('./h:xgrg', ns):
                # Aspektipaarik
                for xa_element in xgrg_element.findall('./h:xa', ns):
                    xa = xa_element.text
                    lexemenotes.append(data_classes.Lexemenote(
                        value='Aspektipaarik: ' + xa,
                        lang=xml_helpers.map_lang_codes(lang),
                        publicity=True,
                        sourceLinks=sourcelinks
                    ))
                # Vormikood
                for xvk_element in xgrg_element.findall('./h:xvk', ns):
                    xvl = xvk_element.text
                    lexemenotes.append(data_classes.Lexemenote(
                        value='Vormikood: ' + xvl,
                        lang=xml_helpers.map_lang_codes(lang),
                        publicity=True,
                        sourceLinks=sourcelinks
                    ))
                # Sõnaliik
                for xsl_element in xgrg_element.findall('./h:xsl', ns):
                    xsl = xsl_element.text
                    lexemenotes.append(data_classes.Lexemenote(
                        value='Sõnaliik: ' + xsl,
                        lang=xml_helpers.map_lang_codes(lang),
                        publicity=True,
                        sourceLinks=sourcelinks
                    ))
                # Gr sugu (sks)
                for xzde_element in xgrg_element.findall('./h:xzde', ns):
                    xzde = xzde_element.text
                    lexemenotes.append(data_classes.Lexemenote(
                        value='Grammatiline sugu (saksa): ' + xzde,
                        lang=xml_helpers.map_lang_codes(lang),
                        publicity=True,
                        sourceLinks=sourcelinks
                    ))
                # Gr sugu (vene)
                for xzru_element in xgrg_element.findall('./h:xzru', ns):
                    xzru = xzru_element.text
                    lexemenotes.append(data_classes.Lexemenote(
                        value='Grammatiline sugu (vene): ' + xzru,
                        lang=xml_helpers.map_lang_codes(lang),
                        publicity=True,
                        sourceLinks=sourcelinks
                    ))

            # Allikas
            for all_element in xg_element.findall('./h:all', ns):
                if all_element.text:
                    sources_from_xp.append(all_element.text)
                    word_sourcelinks.append(data_classes.Sourcelink(
                        sourceId=xml_helpers.get_source_id_by_source_text(sources_with_ids, all_element.text),
                        value=all_element.text,
                        name=''
                    ))

            words.append(data_classes.Word(
                valuePrese=lexemevalue,
                lang=xml_helpers.map_lang_codes(lang),
                lexemePublicity=True,
                lexemeValueStateCode=valuestatecode,
                wordTypeCodes=wordtypecodes,
                lexemeNotes=lexemenotes,
                lexemeSourceLinks=word_sourcelinks
            ))

    return words, definitions, sources_from_xp


def ter_word(sources_with_ids, a_element):
    words = []
    concept_notes = []
    for terg_element in a_element.findall('.//h:terg', ns):
        lang = 'est'
        valuestatecode = None
        sourcelinks = []
        lexemenotes = []
        wordtypecodes = []

        for ter_element in terg_element.findall('./h:ter', ns):

            if '[' in ter_element.text and '?' not in ter_element.text:
                words.append(data_classes.Word(
                    valuePrese=ter_element.text.replace('[', '').replace(']', ''),
                    lang='est',
                    lexemePublicity=True,
                    lexemeValueStateCode=None,
                    wordTypeCodes=[],
                    lexemeNotes=[],
                    lexemeSourceLinks=[]
                ))

            value = re.sub(r'\[.*?\]', '', ter_element.text)

            # Vaste liik
            liik = ter_element.attrib.get(f'{{{ns["h"]}}}liik', '')
            if liik:
                if liik == 'l':
                    wordtypecodes.append(liik)

            # Vaste tüüp
            tyyp = ter_element.attrib.get(f'{{{ns["h"]}}}tyyp', '')
            if tyyp:
                if tyyp == 'ee':
                    valuestatecode = 'eelistatud'
                else:
                    valuestatecode = None

        for s in terg_element.findall('./h:s', ns):

            if s.text == 'halb':
                valuestatecode = 'väldi'
            elif s.text == 'van':
                valuestatecode = 'vananenud'
            elif s.text == 'kõnek':
                break
            elif s.text == 'aj':
                concept_notes.append(data_classes.Note(
                    value='Ajalooline mõiste',
                    lang='est',
                    publicity=True,
                    sourceLinks=[]
                ))
            else:
                break

        for e in terg_element.findall('./h:etym', ns):
            lexemenote = data_classes.Lexemenote(
                value='Lähtekeel: ' + e.text,
                lang='est',
                publicity=True,
                sourceLinks=[]
            )
            lexemenotes.append(lexemenote)

        # Eestikeelse termini allikaviide
        for all_element in terg_element.findall('./h:all', ns):
            source_value = all_element.text
            sourcelink = data_classes.Sourcelink(
                sourceId=xml_helpers.get_source_id_by_source_text(sources_with_ids, source_value),
                value=source_value,
                name='')
            sourcelinks.append(sourcelink)

        word = data_classes.Word(valuePrese=value,
                                 lang=lang,
                                 lexemePublicity=True,
                                 lexemeValueStateCode=valuestatecode,
                                 wordTypeCodes=wordtypecodes,
                                 lexemeNotes=lexemenotes,
                                 lexemeSourceLinks=sourcelinks)
        words.append(word)

    return words, concept_notes


