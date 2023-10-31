import helpers
import parse_har_concepts

file_path = 'har/__sr/har/har1.xml'
prettified_file = 'har/__sr/har/beautified_har.xml'
output_json = 'har/__sr/har/har.json'

#helpers.beautify_xml(file_path, prettified_file)
parse_har_concepts.parse_xml(prettified_file, output_json)