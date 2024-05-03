# EE WORDS

import xml_helpers
import data_classes

ns = {
    'x': 'http://www.eki.ee/dict/has',
    'xml': 'http://www.w3.org/XML/1998/namespace'
}

def ter_word(a_element, sources_with_ids):
    words = []
    for terg_element in a_element.findall('.//x:terg', ns):
        valuestatecode = None
        sourcelinks = []
        lexemenotes = []
        wordtypecodes = []

        etym_element = terg_element.find('.//x:etym', ns)
        etym_text = etym_element.text if etym_element is not None else None

        for ter_element in terg_element.findall('./x:ter', ns):
            value = ter_element.text.replace('&ema;', '<eki-foreign>').replace('&eml;', '</eki-foreign>')
            liik = ter_element.attrib.get(f'{{{ns["x"]}}}liik', '')

            # Process wordtypecode
            if liik and liik == 'z':
                lang = 'est'
                wordtypecodes.append('z')
                value = '<eki-foreign>' + value + '</eki-foreign>'
            elif liik and liik == 'l':
                wordtypecodes.append('l')
            else:
                lang = 'est'

            if etym_text:
                lexemenotes.append(data_classes.Lexemenote(
                    value='Päritolu: ' + xml_helpers.map_lang_acronyms(etym_text),
                    lang='est',
                    publicity=True,
                    sourceLinks=[]
                ))

            # Vaste tüüp
            tyyp = ter_element.attrib.get(f'{{{ns["x"]}}}tyyp', '')
            if tyyp:
                if tyyp == 'ee':
                    valuestatecode = 'eelistatud'
                else:
                    valuestatecode = None

            for s_element in terg_element.findall('./x:s', ns):
                if s_element.text:
                    if s_element.text == 'halb':
                        valuestatecode = 'väldi'
                    elif s_element.text == 'van':
                        valuestatecode = 'endine'
                    else:
                        lexemenotes.append(data_classes.Lexemenote(
                            value='Stiil: ' + s_element.text,
                            lang=xml_helpers.map_lang_codes(lang),
                            publicity=True,
                            sourceLinks=sourcelinks
                        ))
            for mrk_el in terg_element.findall('./x:mrk', ns):
                if mrk_el.text:
                    if mrk_el.text.startswith('['):
                        s_id, s_value, s_inner = xml_helpers.get_source_id_and_name_by_source_text(sources_with_ids,
                                                                                                   mrk_el.text.strip(
                                                                                                       '[]'))
                        source = data_classes.Sourcelink(
                            sourceId=s_id,
                            value=s_value,
                            name=s_inner
                        )
                        sourcelinks.append(source)
                    else:
                        lexemenotes.append(data_classes.Lexemenote(
                            value=mrk_el.text,
                            lang='est',
                            publicity=False,
                            sourceLinks=None
                        ))

        for h in terg_element.findall('./x:hld', ns):
            lexemenote = data_classes.Lexemenote(
                value='Hääldus: ' + h.text,
                lang='est',
                publicity=True,
                sourceLinks=[]
            )
            lexemenotes.append(lexemenote)

        # Eestikeelse termini allikaviide
        for all_element in terg_element.findall('./x:all', ns):
            source_value = all_element.text
            sourcelink = data_classes.Sourcelink(sourceId=121611, value=source_value, name='')
            sourcelinks.append(sourcelink)

        word = data_classes.Word(valuePrese=value.replace('&ema;', '<eki-foreign>').replace('&eml;', '</eki-foreign>'),
                                 lang=lang,
                                 lexemePublicity=True,
                                 lexemeValueStateCode=valuestatecode,
                                 wordTypeCodes=wordtypecodes,
                                 lexemeNotes=lexemenotes,
                                 lexemeSourceLinks=sourcelinks)
        words.append(word)

    if len(words) == 1 and words[0].lexemeValueStateCode == 'eelistatud':
        print(words)
        words[0].lexemeValueStateCode = None
    else:
        first_found = False

        for w in words:
            if w.lexemeValueStateCode == 'eelistatud':
                if not first_found:
                    first_found = True
                else:
                    w.lexemeValueStateCode = None

    return words