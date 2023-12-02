from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
import data_classes

ns = {'h': 'http://www.eki.ee/dict/har'}

# Function to parse XML and create Concept objects
def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    concepts = []

    for a_element in root.findall('.//h:A', ns):
        words = []
        definitions = []

        # Eestikeelsed terminid
        for ter_element in a_element.findall('.//h:ter', ns):
            value = ter_element.text
            lang = 'est'

            word = data_classes.Word(value=value, lang=lang)
            words.append(word)

        # Võõrkeelsed vasted
        for xp_element in a_element.findall('.//h:xp', ns):
            lang = xp_element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', 'unknown')

            for x_element in xp_element.findall('.//h:x', ns):
                value = x_element.text
                word = data_classes.Word(value=value, lang=lang)
                words.append(word)

        # Võõrkeelsed kaudtõlked
        for xp_element in a_element.findall('.//h:xp', ns):
            lang = xp_element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', 'unknown')

            for xqd_element in xp_element.findall('.//h:xqd', ns):
                value = x_element.text

                word = data_classes.Word(
                    value=value,
                    lang=lang,
                    lexemeNotes=data_classes.Lexemenote(
                        value='Kaudtõlge',
                        lang='est',
                        publicity='True',
                        sourceLinks=None
                    )
                )
                words.append(word)

        # Definitsioonid
        for tg_element in a_element.findall('.//h:tg', ns):
            for def_element in tg_element.findall('.//h:def', ns):

                value = def_element.text
                print(value)
                definition = data_classes.Definition(value=value, lang='est', definitionTypeCode='definitsioon',sourceLinks=None)
                definitions.append(definition)

        concept = data_classes.Concept(
            datasetCode='har-02-12',
            manualEventOn=None,
            manualEventBy=None,
            firstCreateEventOn=None,
            firstCreateEventBy=None,
            definitions=definitions,
            words=words
        )
        concepts.append(concept)

    return concepts