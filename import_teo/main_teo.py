import parse_xml
import xml_helpers
import helpers

input_xml_file_path = "__sr/teo/teo1.xml"
prettified_xml_file_path = "__sr/teo/teo1_prettified.xml"
output_json_file_path = '__sr/teo/teo1.json'

#helpers.beautify_xml(input_xml_file_path, prettified_xml_file_path)

concepts = parse_xml.parse_xml(prettified_xml_file_path)

xml_helpers.write_dicts_to_json_file(concepts, output_json_file_path)