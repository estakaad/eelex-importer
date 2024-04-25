# VÕÕRKEELSED TERMINID

import data_classes
import sources_helpers
import xml_helpers


# Vastete plokk
def xp_to_words(a_element, sources_with_ids, ns):
    words = []
    sourcelinks = []
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
            wordtypecodes = []

            # Vaste
            for x_element in xg_element.findall('./h:x', ns):
                lexemevalue = x_element.text


                liik = x_element.attrib.get(f'{{{ns["h"]}}}liik', '')
                if liik:
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
                        valuestatecode = 'endine'
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
                    note_value = co_element.text
                    if 'ba;' in co_element.text:

                        note_value = co_element.text.replace('&ba;', '<eki-highlight>').replace('&bl;', '</eki-highlight>')
                    if '[EKSPERT]' in note_value:
                        if sources_helpers.get_source_id_and_name_by_source_text(sources_with_ids, 'Ekspert'):
                            s_id, s_name, s_inner = sources_helpers.get_source_id_and_name_by_source_text(sources_with_ids, 'Ekspert')

                            lexemenotes.append(data_classes.Lexemenote(
                                value=note_value.replace(' [EKSPERT]', ''),
                                lang=xml_helpers.map_lang_codes(co_lang),
                                publicity=True,
                                sourceLinks=[data_classes.Sourcelink(
                                    sourceId=s_id,
                                    value=s_name,
                                    name=s_inner
                                )]
                            ))
                        else:
                            print('EKSPERT puudu: ' + co_element.text)


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
                    if 'Tammets' in mrk_value:
                        source_id, source_name, s_inner = sources_helpers.get_source_id_and_name_by_source_text(
                            sources_with_ids, 'Tammets, K; Laanpere, M. (2015). Õpianalüütika kontseptuaalne raamistik ja selle rakendatavus Eesti kontekstis. Eesti Haridusteaduste Ajakiri, 3 (2)')
                        word_sourcelinks.append(data_classes.Sourcelink(
                            sourceId=source_id,
                            value=source_name,
                            name='216-246'
                        ))
                    elif '];' in mrk_value:
                        sources_from_mrk = mrk_value.split(';')
                        for s in sources_from_mrk:
                            cleaned = s.strip().strip('[').strip(']')
                            source_id, source_name, s_inner = sources_helpers.get_source_id_and_name_by_source_text(sources_with_ids, cleaned)
                            word_sourcelinks.append(data_classes.Sourcelink(
                                sourceId=source_id,
                                value=source_name,
                                name=s_inner
                            ))
                    elif '] [' in mrk_value:
                        sources_from_mrk = mrk_value.split('] [')
                        for s in sources_from_mrk:
                            cleaned = s.strip().strip('[').strip(']')
                            source_id, source_name, s_inner = sources_helpers.get_source_id_and_name_by_source_text(sources_with_ids, cleaned)
                            word_sourcelinks.append(data_classes.Sourcelink(
                                sourceId=source_id,
                                value=source_name,
                                name=s_inner
                            ))
                    elif '; ' in mrk_value:
                        sources_from_mrk = mrk_value.split('; ')
                        for s in sources_from_mrk:
                            cleaned = s.strip().strip('[').strip(']')
                            source_id, source_name, s_inner = sources_helpers.get_source_id_and_name_by_source_text(sources_with_ids, cleaned)
                            word_sourcelinks.append(data_classes.Sourcelink(
                                sourceId=source_id,
                                value=source_name,
                                name=s_inner
                            ))
                    else:
                        cleaned = mrk_value.strip('[]')
                        source_id, source_name, s_inner = sources_helpers.get_source_id_and_name_by_source_text(sources_with_ids,
                                                                                                       cleaned)
                        word_sourcelinks.append(data_classes.Sourcelink(
                            sourceId=source_id,
                            value=source_name,
                            name=s_inner
                        ))
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
                        value='Grammatiline sugu: ' + xzde,
                        lang=xml_helpers.map_lang_codes(lang),
                        publicity=False,
                        sourceLinks=sourcelinks
                    ))
                # Gr sugu (vene)
                for xzru_element in xgrg_element.findall('./h:xzru', ns):
                    xzru = xzru_element.text
                    lexemenotes.append(data_classes.Lexemenote(
                        value='Grammatiline sugu: ' + xzru,
                        lang=xml_helpers.map_lang_codes(lang),
                        publicity=False,
                        sourceLinks=sourcelinks
                    ))

            # Allikas
            for all_element in xg_element.findall('./h:all', ns):
                if all_element.text:
                    sources_from_xp.append(all_element.text)
                    s_id, s_name, s_inner = sources_helpers.get_source_id_and_name_by_source_text(sources_with_ids, all_element.text)
                    word_sourcelinks.append(data_classes.Sourcelink(
                        sourceId=s_id,
                        value=s_name,
                        name=s_inner
                    ))

            if lexemevalue:
                if lexemevalue.startswith('(VFs) '):
                    lexemevalue = lexemevalue.replace('(VFs) ', '')
                    lexemenotes.append(data_classes.Lexemenote(
                        value='Vene Föderatsioonis',
                        lang='est',
                        publicity=True,
                        sourceLinks=[]
                    ))
                elif lexemevalue.startswith('(VFs ametlikult) '):
                    lexemevalue = lexemevalue.replace('(VFs ametlikult) ', '')
                    lexemenotes.append(data_classes.Lexemenote(
                        value='Vene Föderatsioonis ametlikult',
                        lang='est',
                        publicity=True,
                        sourceLinks=[]
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