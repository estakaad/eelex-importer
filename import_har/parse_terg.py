# EESTIKEELSED TERMINID JA MÕISTE MÄRKUSED

import data_classes
import sources_helpers
import xml_helpers
import re

def ter_word(sources_with_ids, a_element, ns):

    # Terminid
    words = []
    # Mõiste märkused
    concept_notes = []

    # Ühe termini grupid
    for terg_element in a_element.findall('.//h:terg', ns):
        lang = 'est'
        valuestatecode = None
        sourcelinks = []
        lexemenotes = []
        wordtypecodes = []

        # Termin
        for ter_element in terg_element.findall('./h:ter', ns):

            # Kui termin sisaldab [], siis tuleb teha mitu keelendit
            if '[' in ter_element.text and '?' not in ter_element.text:
                # Eemaldada nurksulud ja lisada too pikem termin
                words.append(data_classes.Word(
                    valuePrese=ter_element.text.replace('[', '').replace(']', ''),
                    lang='est',
                    lexemePublicity=True,
                    lexemeValueStateCode=None,
                    wordTypeCodes=[],
                    lexemeNotes=[],
                    lexemeSourceLinks=[]
                ))

            # Eemaldada nurksulud ja nende vahel olev, et lisada lühem termin
            value = re.sub(r'\[.*?\]', '', ter_element.text)

            # Vaste liik
            liik = ter_element.attrib.get(f'{{{ns["h"]}}}liik', '')

            if liik:
                if liik == 'l':
                    wordtypecodes.append(liik)
                elif liik == 'z':
                    wordtypecodes.append(liik)

            # Vaste tüüp
            tyyp = ter_element.attrib.get(f'{{{ns["h"]}}}tyyp', '')
            if tyyp:
                if tyyp == 'ee':
                    valuestatecode = 'eelistatud'
                else:
                    valuestatecode = None

        # Stiil
        for s in terg_element.findall('./h:s', ns):
            if s.text == 'halb':
                valuestatecode = 'väldi'
            elif s.text == 'van':
                valuestatecode = 'endine'
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

        # Etümoloogia - läheb märkuseks
        for e in terg_element.findall('./h:etym', ns):
            lexemenote = data_classes.Lexemenote(
                value='Lähtekeel: ' + xml_helpers.map_lang_codes_to_names(e.text),
                lang='est',
                publicity=True,
                sourceLinks=[]
            )
            lexemenotes.append(lexemenote)

        # Termini allikaviited
        for all_element in terg_element.findall('./h:all', ns):
            source_value = all_element.text
            if sources_helpers.get_source_id_and_name_by_source_text(sources_with_ids, source_value):
                s_id, s_name, s_inner = sources_helpers.get_source_id_and_name_by_source_text(sources_with_ids, source_value)
                sourcelink = data_classes.Sourcelink(
                    sourceId=s_id,
                    value=s_name,
                    name=s_inner)
                sourcelinks.append(sourcelink)
            else:
                print('Puuduv allikas: ' + source_value)

        word = data_classes.Word(valuePrese=value,
                                 lang=lang,
                                 lexemePublicity=True,
                                 lexemeValueStateCode=valuestatecode,
                                 wordTypeCodes=wordtypecodes,
                                 lexemeNotes=lexemenotes,
                                 lexemeSourceLinks=sourcelinks)
        words.append(word)

    return words, concept_notes