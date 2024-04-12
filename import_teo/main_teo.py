import parse_xml
import xml_helpers
import helpers
import json


# XML PREPROCESSING
input_xml_file_path = "__sr/teo/teo1.xml"
prettified_xml_file_path = "__sr/teo/teo1_prettified.xml"
output_json_file_path = '__sr/teo/teo1.json'
concepts_with_ids = 'files/concepts_saved.json'
meaning_relations_file_path = 'files/meaning_relations_output.json'
dataset_code = 'usu-1204'

#helpers.beautify_xml(input_xml_file_path, prettified_xml_file_path)

# LOAD SOURCES

sources_with_ids = "files/allikad_uute_id_dega.json"
with open(sources_with_ids, 'r', encoding='utf-8') as file:
    sources_data = json.load(file)

# # CREATE CONCEPTS
concepts, relation_links = parse_xml.parse_xml(prettified_xml_file_path, sources_data, dataset_code)
#
# # WRITE CONCEPTS TO JSON FILE
xml_helpers.write_dicts_to_json_file(concepts, output_json_file_path)

# # MEANING RELATIONS WITH GUIDS INSTEAD OF MEANING_IDS
# relation_links_with_all_guids = xml_helpers.find_guid_for_words(concepts, relation_links)
# concepts_data = xml_helpers.load_json_data(concepts_with_ids)
# guid_to_meaningid = xml_helpers.create_guid_to_meaningid_mapping(concepts_data)
# relations_data = xml_helpers.guid_pairs_to_meaning_relations_as_json(relation_links_with_all_guids, guid_to_meaningid)
# xml_helpers.write_meaning_relation_dicts_to_json_file(relations_data, meaning_relations_file_path)

# ADD GRAMMATICAL GENDER TO LEXEMES
