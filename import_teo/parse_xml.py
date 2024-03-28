from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
import data_classes
import xml_helpers


ns = {
    'x': 'http://www.eki.ee/dict/teo',
    'xml': 'http://www.w3.org/XML/1998/namespace'
}

# Function to parse XML and create Concept objects
def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    concepts = []
    relation_links = []

    for a_element in root.findall('.//x:A', ns):
        if a_element.attrib.get(f'{{{ns["x"]}}}as', '') == 'elx':
            continue
        else:
            public_concept = True
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
            for v_element in a_element.findall('.//x:v', ns):
                d_domain = v_element.text
                code = xml_helpers.map_domain_to_lenoch_code(d_domain)
                if code != 'unknown':
                    domain = {
                        'code': code,
                        'origin': 'lenoch'
                    }
                    domains.append(domain)

            # Toimetaja
            for editor in a_element.findall('.//x:T', ns):
                notes.append(data_classes.Note(
                    value='Artikli toimetaja: ' + editor.text,
                    lang='est',
                    publicity=False,
                    sourceLinks=[]
                ))

            for guid in a_element.findall('.//x:G', ns):
                conceptids.append(guid.text)

            if a_element.findall('.//x:TL', ns):
                public_concept = True
            else:
                public_concept = False

            for tg_element in a_element.findall('.//x:tg', ns):
                definition, notes_from_xml, forums_from_xml, links, usages = tg_def_definition(guid.text, tg_element)

                if links:
                    for l in links:
                        relation_links.append(l)

                if definition:
                    definitions.append(definition)

                for note in notes_from_xml:
                    if note.value:
                        notes.append(note)
                for forum in forums_from_xml:
                    if forum.value:
                        forums.append(forum)

            # Kommentaarid (sisemärkusteks)

            for kom_group_element in a_element.findall('.//x:komg', ns):
                for kom_elem in kom_group_element.findall('.//x:kom', ns):
                    content = kom_elem.text
                for kom_aut_elem in kom_group_element.findall('.//x:kaut', ns):
                    author = kom_aut_elem.text

                forum_item = data_classes.Forum(
                    value=content + ' (' + author + ')'
                )

                forums.append(forum_item)

            # Eestikeelsed terminid
            for w in ter_word(a_element):
                words.append(w)

            if usages:
                for w in words:
                    if w.lexemeValueStateCode == 'eelistatud':
                        w.usages=usages

            # Võõrkeelsed vasted

            foreign_words, foreign_definitions = xp_to_words(a_element)

            for w in foreign_words:
                if w.valuePrese:
                    words.append(w)

            for d in foreign_definitions:
                if d.value:
                    definitions.append(d)


            # Koosta mõiste objekt
            concept = data_classes.Concept(
                datasetCode='usu-07-12',
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

            if public_concept == False:
                for n in concept.notes:
                    n.publicity = False
                for w in concept.words:
                    w.lexemePublicity = False
                    for ln in w.lexemeNotes:
                        ln.publicity = False
                    for u in w.usages:
                        u.publicity = False

            concepts.append(concept)

    return concepts, relation_links


# Mõiste tähendusgrupp: tg : def - Definitsiooniks jmt
def tg_def_definition(guid, tg_element):
    def_value = None
    definition = None
    notes = []
    sourcelinks = []
    forums = []
    links = []
    usages = []

    for dg_element in tg_element.findall('./x:dg', ns):
        for def_element in dg_element.findall('./x:def', ns):
            def_value = def_element.text
        for all_element in dg_element.findall('./x:all', ns):
            source_value = all_element.text
            sourcelink = data_classes.Sourcelink(
                sourceId=xml_helpers.get_source_id_by_name(source_value),
                value=source_value,
                name='')
            sourcelinks.append(sourcelink)
        for lisa_element in dg_element.findall('./x:lisa', ns):
            lisa_value = lisa_element.text
            notes.append(data_classes.Note(
                value=lisa_value,
                lang='est',
                publicity=True,
                sourceLinks=sourcelinks
            ))
        for ng_element in dg_element.findall('./x:ng', ns):
            usage_sourcelinks = []
            for nall_element in ng_element.findall('./x:nall', ns):
                sourcelink = data_classes.Sourcelink(
                    sourceId=xml_helpers.get_source_id_by_name(nall_element.text),
                    value=nall_element.text,
                    name=''
                )
                usage_sourcelinks.append(sourcelink)

            for n_element in ng_element.findall('./x:n', ns):

                n_value = n_element.text
                usages.append(data_classes.Usage(
                    value=n_value,
                    lang='est',
                    publicity=True,
                    sourceLinks=usage_sourcelinks
                ))

        for dn_element in dg_element.findall('./x:dn', ns):
            notes.append(data_classes.Note(
                value=dn_element.text,
                lang='est',
                publicity=True,
                sourceLinks=[]
            ))

    for co_element in tg_element.findall('./x:co', ns):
        notes.append(data_classes.Note(
            value=co_element.text,
            lang='est',
            publicity=True,
            sourceLinks=[]
        ))

    # Tesaurus
    for tes_element in tg_element.findall('./x:tes', ns):
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
    evts_vt_ka = []

    for evt_element in tg_element.findall('./x:evt', ns):
        evt_value = evt_element.text if evt_element.text is not None else ""
        evt_attrib_value = evt_element.attrib.get(f'{{{ns["x"]}}}evtl', '')

        if evt_attrib_value == "vt ka":
            if evt_value:
                evts_vt_ka.append(evt_value)
                links.append((guid, evt_value))

    # Sisemärkus
    forum = None
    for mrk_element in tg_element.findall('./x:mrk', ns):
        mrk_maut_value = mrk_element.attrib.get(f'{{{ns["x"]}}}maut', '')
        mrk_maeg_value = mrk_element.attrib.get(f'{{{ns["x"]}}}maeg', '')
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
            sourceLinks=[])

    return definition, notes, forums, links, usages

# Vastete plokk
def xp_to_words(a_element):
    words = []
    definitions = []

    for xp_element in a_element.findall('.//x:xp', ns):
        lang = xp_element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', 'unknown')

        for xg_element in xp_element.findall('./x:xg', ns):
            lexemenotes = []
            wordtypecodes = []
            valuestatecode = None
            lexemevalue = None
            word_sourcelinks = []
            sourcelinks = []

            # Vaste
            for x_element in xg_element.findall('./x:x', ns):
                lexemevalue = x_element.text
                # [existing code for processing x elements]

            # Konfessioon
            for k_element in xg_element.findall('.//x:konf', ns):
                note_value = k_element.text
                lexemenotes.append(data_classes.Lexemenote(
                    value=note_value,
                    lang='est',
                    publicity=True,
                    sourceLinks=[]
                ))

            # for xlyh_element in xg_element.findall('./x:xlyh', ns):
            #     words.append(data_classes.Word(
            #         valuePrese=xlyh_element.text,
            #         lang=xml_helpers.map_lang_codes(lang),
            #         lexemePublicity=True,
            #         lexemeValueStateCode=valuestatecode,
            #         wordTypeCodes=["l"],
            #         lexemeNotes=lexemenotes,
            #         lexemeSourceLinks=word_sourcelinks
            #     ))

            # Kaudtõlge
            for xqd_element in xg_element.findall('./x:xqd', ns):
                def_value = xqd_element.text

                definitions.append(data_classes.Definition(
                    value=def_value,
                    lang=xml_helpers.map_lang_codes(lang),
                    definitionTypeCode='definitsioon',
                    sourceLinks=[]
                ))

            # Stiil
            for s_element in xg_element.findall('./x:s', ns):
                if s_element.text:
                    if s_element.text == 'van':
                        valuestatecode = 'vananenud'
                    else:
                        lexemenotes.append(data_classes.Lexemenote(
                            value=s_element.text,
                            lang='est',
                            publicity=False,
                            sourceLinks=None
                        ))

            # Märkus
            for co_element in xg_element.findall('./x:co', ns):
                co_lang = co_element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', 'unknown')

                if co_element.text:
                    lexemenotes.append(data_classes.Lexemenote(
                        value=co_element.text,
                        lang=xml_helpers.map_lang_codes(co_lang),
                        publicity=True,
                        sourceLinks=sourcelinks
                    ))

            # Sisemärkus (mitteavalik ilmiku märkus)
            for mrk_element in xg_element.findall('./x:mrk', ns):
                mrk_lang_value = mrk_element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', 'unknown')
                mrk_maut_value = mrk_element.attrib.get(f'{{{ns["x"]}}}maut', '')
                mrk_maeg_value = mrk_element.attrib.get(f'{{{ns["x"]}}}maeg', '')

                mrk_value = mrk_element.text

                lexemenotes.append(data_classes.Lexemenote(
                    value=mrk_value + ' (' + mrk_maut_value + ', ' + mrk_maeg_value + ')',
                    lang=xml_helpers.map_lang_codes(mrk_lang_value),
                    publicity=False,
                    sourceLinks=[]
                ))

            # Grammatika grupp
            for xgrg_element in xg_element.findall('./x:xgrg', ns):
                # Aspektipaarik
                for xa_element in xgrg_element.findall('./x:xa', ns):
                    xa = xa_element.text
                    lexemenotes.append(data_classes.Lexemenote(
                        value='Aspektipaarik: ' + xa,
                        lang=xml_helpers.map_lang_codes(lang),
                        publicity=True,
                        sourceLinks=sourcelinks
                    ))
                # # Vormikood
                # for xvk_element in xgrg_element.findall('./x:xvk', ns):
                #     xvl = xvk_element.text
                #     lexemenotes.append(data_classes.Lexemenote(
                #         value='Vormikood: ' + xvl,
                #         lang=xml_helpers.map_lang_codes(lang),
                #         publicity=True,
                #         sourceLinks=sourcelinks
                #     ))

                # Sõnaliik
                for xsl_element in xgrg_element.findall('./x:xsl', ns):
                    xsl = xsl_element.text
                    lexemenotes.append(data_classes.Lexemenote(
                        value='Sõnaliik: ' + xsl,
                        lang=xml_helpers.map_lang_codes(lang),
                        publicity=True,
                        sourceLinks=sourcelinks
                    ))
                # Gr sugu (sks)
                for xzde_element in xgrg_element.findall('./x:xzde', ns):
                    xzde = xzde_element.text
                    lexemenotes.append(data_classes.Lexemenote(
                        value='Grammatiline sugu: ' + xzde,
                        lang=xml_helpers.map_lang_codes(lang),
                        publicity=True,
                        sourceLinks=sourcelinks
                    ))
                # Gr sugu (vene)
                for xzru_element in xgrg_element.findall('./x:xzru', ns):
                    xzru = xzru_element.text
                    lexemenotes.append(data_classes.Lexemenote(
                        value='Grammatiline sugu: ' + xzru,
                        lang=xml_helpers.map_lang_codes(lang),
                        publicity=True,
                        sourceLinks=sourcelinks
                    ))

            # Allikas
            for all_element in xg_element.findall('./x:all', ns):
                if all_element.text:
                    word_sourcelinks.append(data_classes.Sourcelink(
                        sourceId=xml_helpers.get_source_id_by_name(all_element.text),
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

    return words, definitions


def ter_word(a_element):
    words = []
    for terg_element in a_element.findall('.//x:terg', ns):
        ekeel_value = ''
        ex_value = ''
        ek_value = ''
        ed_value = ''
        etvk_value = ''

        etym_element = terg_element.find('.//x:etym', ns)
        lang = xml_helpers.map_lang_codes(etym_element.text) if etym_element is not None else "est"

        valuestatecode = None
        sourcelinks = []
        lexemenotes = []
        wordtypecodes = []

        # Termin ja väärtusolek
        for ter_element in terg_element.findall('./x:ter', ns):
            value = ter_element.text
            tyyp_value = ter_element.get('{' + ns['x'] + '}tyyp')
            if tyyp_value == 'ee':
                valuestatecode = 'eelistatud'

        # Konfessioon
        for k_element in terg_element.findall('.//x:konf', ns):
            lexemenotes.append(data_classes.Lexemenote(
                value=k_element.text,
                lang='est',
                publicity=True,
                sourceLinks=None
            ))

        tall_element = terg_element.find('./x:tall', ns)
        if tall_element is not None:
            tall_value = tall_element.text
            sourcelinks.append(data_classes.Sourcelink(
                sourceId=xml_helpers.get_source_id_by_name(tall_value),
                value=tall_value,
                name=None
            ))

            # # Vaste liik
            # liik = ter_element.attrib.get(f'{{{ns["x"]}}}liik', '')
            # if liik:
            #     if liik == 'l':
            #         wordtypecodes.append(liik)
            #     elif liik == 'z':
            #         wordtypecodes.append(liik)

            # Vaste tüüp
            tyyp = ter_element.attrib.get(f'{{{ns["x"]}}}tyyp', '')
            if tyyp:
                if tyyp == 'ee':
                    valuestatecode = 'eelistatud'
                else:
                    valuestatecode = None

        for etg in terg_element.findall('./x:etg', ns):
            for etgg in etg.findall('./x:etgg', ns):
                for ekeel in etgg.findall('./x:ekeel', ns):
                    ekeel_value = ekeel.text
                for ex in etgg.findall('./x:ex', ns):
                    ex_value = '<eki-foreign>' + ex.text + '</eki-foreign>'
                for ed in etgg.findall('./x:ed', ns):
                    ed_value = "'" + ed.text + "'"
                for etvk in etgg.findall('./x:etvk', ns):
                    etvk_value = '(' + etvk.text + ')'
            for ek in etg.findall('./x:ek', ns):
                ek_value = ek.text

            etymology_values = [value for value in [ekeel_value, ex_value, ek_value, ed_value, etvk_value] if value]

            etymology_string = ' '.join(etymology_values)

            if etymology_values:
                lexemenote = data_classes.Lexemenote(
                    value='Etümoloogia: ' + etymology_string,
                    lang='est',
                    publicity=True,
                    sourceLinks=[]
                )
                lexemenotes.append(lexemenote)

        # for h in terg_element.findall('./x:hld', ns):
        #     lexemenote = data_classes.Lexemenote(
        #         value='Hääldus: ' + h.text,
        #         lang='est',
        #         publicity=True,
        #         sourceLinks=[]
        #     )
        #     lexemenotes.append(lexemenote)

        for s in terg_element.findall('./x:s', ns):
            if s.text == 'van':
                valuestatecode = 'vananenud'
            else:
                lexemenotes.append(data_classes.Lexemenote(
                    value=s.text,
                    lang='est',
                    publicity=False,
                    sourceLinks=None
                ))

        # Eestikeelse termini allikaviide
        for all_element in terg_element.findall('./x:all', ns):
            source_value = all_element.text
            sourcelink = data_classes.Sourcelink(sourceId=xml_helpers.get_source_id_by_name(source_value), value=source_value, name='')
            sourcelinks.append(sourcelink)

        word = data_classes.Word(valuePrese=value,
                                 lang=lang,
                                 lexemePublicity=True,
                                 lexemeValueStateCode=valuestatecode,
                                 wordTypeCodes=wordtypecodes,
                                 lexemeNotes=lexemenotes,
                                 lexemeSourceLinks=sourcelinks)
        words.append(word)

    return words