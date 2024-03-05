import parse_xml
import xml_helpers

dataset_code = 'har-22-02'
input_xml_file_path = "har/__sr/har/beautified_har.xml"
output_json_file_path = 'har/__sr/har/har.json'
sources_file_path = 'har/__sr/har/sources.json'
new_sources = 'har/__sr/har/sources_new.json'

#sources_helpers.sanitise_sources_file(sources_file_path, new_sources)

concepts = parse_xml.parse_xml(dataset_code, input_xml_file_path, new_sources)

#xml_helpers.write_dicts_to_json_file(concepts, output_json_file_path)