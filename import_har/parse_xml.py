from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
import data_classes
import xml_helpers


ns = {
    'h': 'http://www.eki.ee/dict/har',
    'xml': 'http://www.w3.org/XML/1998/namespace'
}

# Function to parse XML and create Concept objects
def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    concepts = []

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
            #d_domain = v_element.text
            d_domain = 'ED1'
            d_origin = 'lenoch'
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

        # Viimase muutmise aeg -
        for last_edit in a_element.findall('.//h:TA', ns):
            manualEventOn = last_edit.text
            date_part = manualEventOn.split("T")[0]
            parts = date_part.split("-")
            manualEventOn = f"{parts[2]}.{parts[1]}.{parts[0]}"

        # Viimane muutja
        for editor in a_element.findall('.//h:T', ns):
            manualEventBy = editor.text

        for tg_element in a_element.findall('.//h:tg', ns):
            definition, notes_from_xml, forums_from_xml = tg_def_definition(tg_element)
            definitions.append(definition)
            for note in notes_from_xml:
                notes.append(note)
            for forum in forums_from_xml:
                forums.append(forum)

        # Kommentaarid (sisemärkusteks)

        for kom_group_element in a_element.findall('.//h:komg', ns):
            for kom_elem in kom_group_element.findall('.//h:kom', ns):
                content = kom_elem.text
            for kom_aut_elem in kom_group_element.findall('.//h:kaut', ns):
                author = kom_aut_elem.text
            for kom_t_elem in kom_group_element.findall('.//h:kaeg', ns):
                time = kom_t_elem.text

            forum_item = data_classes.Forum(
                value=content + ' (' + author + ', ' + time + ')'
            )

            forums.append(forum_item)

        # Eestikeelsed terminid
        for w in ter_word(a_element):
            words.append(w)

        # Võõrkeelsed vasted
        for w in xp_to_words(a_element):
            words.append(w)

        # Koosta mõiste objekt
        concept = data_classes.Concept(
            datasetCode='har-03-12',
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

    return concepts


# Mõiste tähendusgrupp: tg : def - Definitsiooniks jmt
def tg_def_definition(tg_element):
    def_value = None
    definition = None
    notes = []
    sourcelinks = []
    forums = []

    for dg_element in tg_element.findall('./h:dg', ns):
        for def_element in dg_element.findall('./h:def', ns):
            def_value = def_element.text
        for all_element in dg_element.findall('./h:all', ns):
            source_value = all_element.text
            sourcelink = data_classes.Sourcelink(
                sourceId=121611,
                value=source_value,
                name='')
            sourcelinks.append(sourcelink)
        for dn_element in dg_element.findall('./h:dn', ns):
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

    # Tesaurus
    for tes_element in tg_element.findall('./h:tes', ns):
        for child in tes_element:
            tag_name = child.tag.split('}')[-1]

            child_text = child.text if child.text is not None else ""

            notes.append(data_classes.Note(
                value=tag_name + ": " + child_text,
                lang='est',
                publicity=True,
                sourceLinks=[]
            ))

    # Edasiviited
    evts_vrd = []
    evts_vt_ka = []

    for evt_element in tg_element.findall('./h:evt', ns):
        evt_value = evt_element.text if evt_element.text is not None else ""
        evt_attrib_value = evt_element.attrib.get(f'{{{ns["h"]}}}evtl', '')

        if evt_attrib_value == "vrd":
            evts_vrd.append(evt_value)
        elif evt_attrib_value == "vt ka":
            evts_vt_ka.append(evt_value)

    if evts_vrd:
        combined_evts_vrd = ', '.join(evts_vrd)
        notes_value_vrd = f"Vrd: {combined_evts_vrd}"

        note_vrd = data_classes.Note(
            value=notes_value_vrd,
            lang='est',
            publicity=True,
            sourceLinks=[]
        )
        notes.append(note_vrd)

    if evts_vt_ka:
        combined_evts_vt_ka = ', '.join(evts_vt_ka)
        notes_value_vt_ka = f"Vt ka: {combined_evts_vt_ka}"

        note_vt_ka = data_classes.Note(
            value=notes_value_vt_ka,
            lang='est',
            publicity=True,
            sourceLinks=[]
        )
        notes.append(note_vt_ka)

    # Sisemärkus
    forum = None
    for mrk_element in tg_element.findall('./h:mrk', ns):
        mrk_maut_value = mrk_element.attrib.get(f'{{{ns["h"]}}}maut', '')
        mrk_maeg_value = mrk_element.attrib.get(f'{{{ns["h"]}}}maeg', '')
        forum_value = mrk_element.text
        forum = data_classes.Forum(
            value=forum_value + ' (' + mrk_maut_value + ', ' + mrk_maeg_value + ')'
        )

    if forum is not None:
        forums.append(forum)

    if def_value:
        definition = data_classes.Definition(
            value=def_value,
            lang='est',
            definitionTypeCode='definitsioon',
            sourceLinks=sourcelinks)

    return definition, notes, forums

# Vastete plokk
def xp_to_words(a_element):
    words = []
    sourcelinks = []
    wordtypecodes = []
    valuestatecode = None
    lexemevalue = None

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
                    print(liik)
                    if liik == 'l':
                        wordtypecodes.append(liik)

                # Vaste tüüp
                tyyp = x_element.attrib.get(f'{{{ns["h"]}}}tyyp', '')
                if tyyp:
                    if tyyp == 'ee':
                        valuestatecode = 'eelistatud'
                    else:
                        valuestatecode = None
            # Stiil
            for s_element in xg_element.findall('./h:s', ns):
                if s_element.text:
                    lexemenotes.append(data_classes.Lexemenote(
                        value='Stiil: ' + s_element.text,
                        lang=xml_helpers.map_lang_codes(lang),
                        publicity=True,
                        sourceLinks=sourcelinks
                    ))

            # Märkus
            for co_element in xg_element.findall('./h:co', ns):
                co_lang = co_element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', 'unknown')

                print(co_lang)

                if co_element.text:
                    lexemenotes.append(data_classes.Lexemenote(
                        value=co_element.text,
                        lang=xml_helpers.map_lang_codes(co_lang),
                        publicity=True,
                        sourceLinks=sourcelinks
                    ))

            # Sisemärkus (mitteavalik ilmiku märkus)
            for mrk_element in xg_element.findall('./h:mrk', ns):
                mrk_lang_value = mrk_element.attrib.get(f'{{{ns["h"]}}}lang', '')
                mrk_maut_value = mrk_element.attrib.get(f'{{{ns["h"]}}}maut', '')
                mrk_maeg_value = mrk_element.attrib.get(f'{{{ns["h"]}}}maeg', '')

                mrk_value = mrk_element.text

                lexemenotes.append(data_classes.Lexemenote(
                    value=mrk_value + ' (' + mrk_maut_value + ', ' + mrk_maeg_value + ')',
                    lang=xml_helpers.map_lang_codes(mrk_lang_value),
                    publicity=False,
                    sourceLinks=None
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
                    word_sourcelinks.append(data_classes.Sourcelink(
                        sourceId=xml_helpers.get_source_id_by_name(all_element.text),
                        value=all_element.text,
                        name=''
                    ))

            words.append(data_classes.Word(
                value=lexemevalue,
                lang=xml_helpers.map_lang_codes(lang),
                lexemePublicity=True,
                lexemeValueStateCode=valuestatecode,
                wordTypeCodes=wordtypecodes,
                lexemeNotes=lexemenotes,
                lexemeSourceLinks=word_sourcelinks
            ))

    return words



def ter_word(a_element):
    words = []
    for terg_element in a_element.findall('.//h:terg', ns):
        lang = 'est'
        valuestatecode = None
        sourcelinks = []
        lexemenotes = []

        for ter_element in terg_element.findall('./h:ter', ns):
            value = ter_element.text

        for s in terg_element.findall('./h:s', ns):
            if s.text == 'van':
                print(value)
                valuestatecode = 'endine'

        for h in terg_element.findall('./h:hld', ns):
            print(h.text)
            lexemenote = data_classes.Lexemenote(
                value='Hääldus: ' + h.text,
                lang='est',
                publicity=True,
                sourceLinks=None
            )
            lexemenotes.append(lexemenote)

        for e in terg_element.findall('./h:etym', ns):
            lexemenote = data_classes.Lexemenote(
                value='Lähtekeel: ' + e.text,
                lang='est',
                publicity=True,
                sourceLinks=None
            )
            lexemenotes.append(lexemenote)

        for grg in terg_element.findall('./h:grg', ns):
            for mv in grg.findall('./h:mv', ns):

                vn_attribute = mv.attrib.get(f'{{{ns["h"]}}}vn')

                if vn_attribute:
                    lexemenote_value = f'Muutevormid: {mv.text}, vorminimi: {vn_attribute}'
                else:
                    lexemenote_value = f'Muutevormid: {mv.text}'

                lexemenote = data_classes.Lexemenote(
                    value=lexemenote_value,
                    lang='est',
                    publicity=True,
                    sourceLinks=None
                )

                lexemenotes.append(lexemenote)

            for vk in grg.findall('./h:vk', ns):
                if vk:
                    lexemenote_value = vk.text
                    lexemenote = data_classes.Lexemenote(
                        value='Vorminimi: ' + lexemenote_value,
                        lang='est',
                        publicity=True,
                        sourceLinks=None
                    )

                    lexemenotes.append(lexemenote)


        # Eestikeelse termini allikaviide
        for all_element in terg_element.findall('./h:all', ns):
            source_value = all_element.text
            sourcelink = data_classes.Sourcelink(sourceId=121611, value=source_value, name='')
            sourcelinks.append(sourcelink)

        word = data_classes.Word(value=value,
                                 lang=lang,
                                 lexemePublicity=True,
                                 lexemeValueStateCode=valuestatecode,
                                 lexemeNotes=lexemenotes,
                                 lexemeSourceLinks=sourcelinks)
        words.append(word)

    return words


