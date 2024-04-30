import parse_xml
import xml_helpers
import sources_helpers
import helpers

dataset_code = 'har'
input_xml_file_path = 'har/__sr/har/har1.xml'
prettified_xml_file_path = "har/__sr/har/beautified_har.xml"
output_json_file_path = 'har/__sr/har/har.json'
sources_file_path = 'har/__sr/har/sources.json'
new_sources = 'har/__sr/har/live_allikad_29042024.json'

concepts_saved = 'har/__sr/har/concepts_saved.json'
relations_with_guids = 'seosed.json'
relations_with_meaning_ids = 'har/__sr/har/relations_with_concept_ids.json'

#helpers.beautify_xml(input_xml_file_path, prettified_xml_file_path)

#sources_helpers.sanitise_sources_file(sources_file_path, new_sources)

concepts = parse_xml.parse_xml(dataset_code, prettified_xml_file_path, new_sources)

xml_helpers.write_dicts_to_json_file(concepts, output_json_file_path)

xml_helpers.replace_guids_with_meaning_ids(relations_with_guids, concepts_saved, relations_with_meaning_ids)