from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
import data_classes
import xml_helpers


ns = {'h': 'http://www.eki.ee/dict/har'}

# Function to parse XML and create Concept objects
def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    concepts = []

    for a_element in root.findall('.//h:A', ns):
        words = []
        notes = []
        definitions = []
        domains = []

        # Valdkonnad
        for v_element in a_element.findall('.//h:v', ns):
            value = v_element.text
            domains.append(value)

        # Eestikeelsed terminid
        for ter_element in a_element.findall('.//h:ter', ns):
            value = ter_element.text
            lang = 'est'
            sourcelinks = []

            # Eestikeelse termini allikaviide
            for all_element in ter_element.findall('.//h:all', ns):
                source_value = all_element.text
                sourcelink = data_classes.Sourcelink(sourceId=121611, value=source_value, name='')
                sourcelinks.append(sourcelink)
                words.append(word)

            word = data_classes.Word(value=value,
                                     lang=lang,
                                     lexemePublicity=True,
                                     lexemeValueStateCode=None,
                                     lexemeNotes=None,
                                     lexemeSourceLinks=sourcelinks)
            words.append(word)

        # Võõrkeelsed vasted
        for xp_element in a_element.findall('.//h:xp', ns):
            lang = xp_element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', 'unknown')

            for xg_element in xp_element.findall('.//h:xg', ns):
                lexemenotes = []

                for x_element in xg_element.findall('.//h:x', ns):
                    value = x_element.text
                    sourcelinks = []

                    # Võõrkeelse vaste allikaviide
                    for all_element in x_element.findall('.//h:all', ns):
                        source_value = all_element.text
                        print(source_value)
                        sourcelink = data_classes.Sourcelink(sourceId=121611, value=source_value, name='')
                        sourcelinks.append(sourcelink)
                        words.append(word)

                for co_element in xg_element.findall('.//h:co', ns):

                    lexemenote_value = co_element.text

                    lexemenotes.append(data_classes.Lexemenote(
                        value=lexemenote_value,
                        lang='est',
                        publicity=True,
                        sourceLinks=sourcelinks))

                word = data_classes.Word(value=value,
                                         lang=xml_helpers.map_lang_codes(lang),
                                         lexemePublicity=True,
                                         lexemeValueStateCode=None,
                                         lexemeNotes=lexemenotes,
                                         lexemeSourceLinks=sourcelinks)
                words.append(word)



        # Võõrkeelsed kaudtõlked
        for xp_element in a_element.findall('.//h:xp', ns):
            lang = xp_element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', 'unknown')

            for xqd_element in xp_element.findall('.//h:xqd', ns):
                value = x_element.text

                sourcelinks = []
                lexemenotes = []

                # Võõrkeelse kaudtõlke allikaviide
                for all_element in xqd_element.findall('.//h:all', ns):
                    source_value = all_element.text
                    sourcelink = data_classes.Sourcelink(
                        sourceId=121611,
                        value=source_value,
                        name='')
                    sourcelinks.append(sourcelink)
                    words.append(word)

                # Võõrkeelse kaudtõlke märkus (sest mujale ei oska seda infot panna)

                lexemenotes.append(data_classes.Lexemenote(
                    value='Kaudtõlge',
                    lang='est',
                    publicity=True,
                    sourceLinks=None
                ))

                word = data_classes.Word(value=value,
                                         lang=xml_helpers.map_lang_codes(lang),
                                         lexemePublicity=True,
                                         lexemeValueStateCode=None,
                                         lexemeNotes=lexemenotes,
                                         lexemeSourceLinks=sourcelinks)
                words.append(word)

        # Definitsioonid
        for tg_element in a_element.findall('.//h:tg', ns):
            sourcelinks = []

            for def_element in tg_element.findall('.//h:def', ns):
                value = def_element.text

            # Definitsiooni allikaviide
            for all_element in tg_element.findall('.//h:all', ns):
                source_value = all_element.text
                sourcelink = data_classes.Sourcelink(
                    sourceId=121611,
                    value=source_value,
                    name='')
                sourcelinks.append(sourcelink)

            definition = data_classes.Definition(
                value=value,
                lang='est',
                definitionTypeCode='definitsioon',
                sourceLinks=sourcelinks)

            definitions.append(definition)

        # Mõiste märkused
        for tg_element in a_element.findall('.//h:tg', ns):

            for co_element in tg_element.findall('.//h:co', ns):
                value = co_element.text

            note = data_classes.Note(
                value=value,
                lang='est',
                publicity=True,
                sourceLinks=sourcelinks)

            notes.append(note)

        concept = data_classes.Concept(
            datasetCode='har-02-12',
            domains=domains,
            manualEventOn=None,
            manualEventBy=None,
            firstCreateEventOn=None,
            firstCreateEventBy=None,
            definitions=definitions,
            notes=notes,
            words=words
        )
        concepts.append(concept)

    return concepts