import parse_xml
import xml_helpers
import sources_helpers


dataset_code = 'har-25-04'
input_xml_file_path = "har/__sr/har/beautified_har.xml"
output_json_file_path = 'har/__sr/har/har.json'
sources_file_path = 'har/__sr/har/sources.json'
new_sources = 'har/__sr/har/sources_with_ids.json'

concepts_saved = 'concepts_saved.json'
relations_with_guids = 'seosed.json'
relations_with_meaning_ids = 'seosed_ids.json'

#sources_helpers.sanitise_sources_file(sources_file_path, new_sources)

concepts = parse_xml.parse_xml(dataset_code, input_xml_file_path, new_sources)

xml_helpers.write_dicts_to_json_file(concepts, output_json_file_path)

#xml_helpers.replace_guids_with_meaning_ids(relations_with_guids, concepts_saved, relations_with_meaning_ids)