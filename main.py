import parse_concepts

file_path = 'teo/__sr/teo/teo1.xml'
prettified_file = 'teo/__sr/teo/beautified_teo.xml'
output_json = 'teo/__sr/teo/beautified_teo.json'

parse_concepts.beautify_xml(file_path, prettified_file)
parse_concepts.parse_xml(prettified_file, output_json)