# FOREIGN WORDS

import data_classes
import xml_helpers


ns = {
    'x': 'http://www.eki.ee/dict/has',
    'xml': 'http://www.w3.org/XML/1998/namespace'
}

def xp_to_words(a_element, sources_with_ids):
    words = []

    definitions = []

    for xp_element in a_element.findall('.//x:xp', ns):
        lang = xp_element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', 'et')

        for xg_element in xp_element.findall('./x:xg', ns):

            wordtypecodes = []
            valuestatecode = None
            lexemevalue = None

            lexemenotes = []
            word_sourcelinks = []

            # Märkus
            for co_element in xg_element.findall('./x:co', ns):
                co_lang = co_element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', 'et')

                lnote_value = co_element.text.replace('&ema;', '<eki-foreign>').replace('&eml;', '</eki-foreign>')

                if co_element.text:
                    lexemenotes.append(data_classes.Lexemenote(
                        value=lnote_value,
                        lang=xml_helpers.map_lang_codes(co_lang),
                        publicity=True,
                        sourceLinks=[]
                    ))

            # Vaste
            for x_element in xg_element.findall('./x:x', ns):
                lexemevalue = x_element.text.replace('&ema;', '<eki-foreign>').replace('&eml;', '</eki-foreign>')

                # Vaste liik
                liik = x_element.attrib.get(f'{{{ns["x"]}}}liik', '')
                if liik:
                    if liik == 'l':
                        wordtypecodes.append(liik)

                # Stiil
                for s_element in xg_element.findall('./x:s', ns):
                    if s_element.text:
                        if s_element.text == 'halb':
                            valuestatecode = 'väldi'
                        if s_element.text == 'van':
                            valuestatecode = 'endine'
                        else:
                            lexemenotes.append(data_classes.Lexemenote(
                                value='Stiil: ' + s_element.text,
                                lang=xml_helpers.map_lang_codes(lang),
                                publicity=False,
                                sourceLinks=[]
                            ))

            # Sisemärkus (mitteavalik ilmiku märkus)
            for mrk_element in xg_element.findall('./x:mrk', ns):

                mrk_lang_value = mrk_element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', 'et')
                mrk_maut_value = mrk_element.attrib.get(f'{{{ns["x"]}}}maut', '')
                mrk_maeg_value = mrk_element.attrib.get(f'{{{ns["x"]}}}maeg', '')

                mrk_value = mrk_element.text

                if mrk_value.startswith('['):

                    s_id, s_value, s_inner = xml_helpers.get_source_id_and_name_by_source_text(sources_with_ids, mrk_value.strip('[]'))

                    word_sourcelinks.append(data_classes.Sourcelink(
                        sourceId=s_id,
                        value=s_value,
                        name=s_inner
                    ))

                else:
                    lexemenotes.append(data_classes.Lexemenote(
                        value=mrk_value + ' (' + mrk_maut_value + ', ' + mrk_maeg_value + ')',
                        lang=xml_helpers.map_lang_codes(mrk_lang_value),
                        publicity=False,
                        sourceLinks=[]
                    ))

            # Grammatika grupp
            for xgrg_element in xg_element.findall('./x:xgrg', ns):

                # Vormikood
                for xvk_element in xgrg_element.findall('./x:xvk', ns):
                    xvl = xvk_element.text
                    lexemenotes.append(data_classes.Lexemenote(
                        value='Vormikood: ' + xvl,
                        lang=xml_helpers.map_lang_codes(lang),
                        publicity=False,
                        sourceLinks=[]
                    ))

                # Sõnaliik
                for xsl_element in xgrg_element.findall('./x:xsl', ns):
                    xsl = xsl_element.text
                    lexemenotes.append(data_classes.Lexemenote(
                        value='Sõnaliik: ' + xsl,
                        lang=xml_helpers.map_lang_codes(lang),
                        publicity=False,
                        sourceLinks=[]
                    ))

                # Gr sugu (sks)
                for xzde_element in xgrg_element.findall('./x:xzde', ns):
                    xzde = xzde_element.text
                    lexemenotes.append(data_classes.Lexemenote(
                        value='Grammatiline sugu: ' + xzde,
                        lang=xml_helpers.map_lang_codes(lang),
                        publicity=False,
                        sourceLinks=[]
                    ))

            # Allikas
            for all_element in xg_element.findall('./x:all', ns):
                if all_element.text:
                    s_id, s_value, s_inner = xml_helpers.get_source_id_and_name_by_source_text(sources_with_ids, all_element.text)
                    word_sourcelinks.append(data_classes.Sourcelink(
                        sourceId=s_id,
                        value=s_value,
                        name=s_inner
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