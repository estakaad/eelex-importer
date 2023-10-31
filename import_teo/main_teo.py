import parse_teo_concepts
import helpers
import import_concepts


dataset_code = 'usu-3110'
file_path = 'teo/__sr/teo/teo1.xml'
prettified_file = 'teo/__sr/teo/beautified_teo.xml'
output_json = 'output-test.json'

#helpers.beautify_xml(file_path, prettified_file)
parse_teo_concepts.parse_xml(prettified_file, output_json, dataset_code)

# Update word ID-s
#import_concepts.update_word_ids(output_json, 'eki', 'usu-3110')

# Import concepts ...