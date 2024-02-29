import parse_xml
import xml_helpers

dataset_code = 'har-22-02'
input_xml_file_path = "har/__sr/har/beautified_har.xml"
output_json_file_path = 'har/__sr/har/har.json'
sources_file_path = 'har/__sr/har/sources.json'

concepts = parse_xml.parse_xml(dataset_code, input_xml_file_path, sources_file_path)

xml_helpers.write_dicts_to_json_file(concepts, output_json_file_path)