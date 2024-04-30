import parse_xml
import xml_helpers
import helpers

input_xml_file_path = "has/__sr/has/has1.xml"
prettified_xml_file_path = "has/__sr/has/has1_prettified.xml"
output_json_file_path = 'has/__sr/has/has1.json'
sources_with_ids_file = 'has/__sr/has/sources_with_ids.json'

#helpers.beautify_xml(input_xml_file_path, prettified_xml_file_path)

sources_with_ids = xml_helpers.load_sources(sources_with_ids_file)

concepts = parse_xml.parse_xml(prettified_xml_file_path, sources_with_ids)

xml_helpers.write_dicts_to_json_file(concepts, output_json_file_path)