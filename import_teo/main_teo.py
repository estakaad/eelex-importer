import parse_xml
import xml_helpers
import helpers

# XML PREPROCESSING
input_xml_file_path = "__sr/teo/teo1.xml"
prettified_xml_file_path = "__sr/teo/teo1_prettified.xml"
output_json_file_path = '__sr/teo/teo1.json'

#helpers.beautify_xml(input_xml_file_path, prettified_xml_file_path)

# CREATE CONCEPTS
concepts, relation_links = parse_xml.parse_xml(prettified_xml_file_path)

# WRITE CONCEPTS TO JSON FILE
xml_helpers.write_dicts_to_json_file(concepts, output_json_file_path)

# MEANING RELATIONS WITH GUIDS INSTEAD OF MEANING_IDS
relation_links_with_all_guids = xml_helpers.find_guid_for_words(concepts, relation_links)