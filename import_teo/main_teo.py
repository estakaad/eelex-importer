import parse_teo_concepts
import helpers

dataset_code = 'usu-3110'
file_path = 'teo/__sr/teo/teo1.xml'
prettified_file = 'teo/__sr/teo/beautified_teo.xml'
output_json = 'teo/__sr/teo/output.json'

#helpers.beautify_xml(file_path, prettified_file)
parse_teo_concepts.parse_xml(prettified_file, output_json, dataset_code)