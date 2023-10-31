import helpers
import import_sources
import log_config
import parse_har_concepts
import json


logger = log_config.get_logger()


file_path = 'har/__sr/har/har1.xml'
prettified_file = 'har/__sr/har/beautified_har.xml'
output_json = 'har/__sr/har/har.json'
sources_without_ids = 'har/__sr/har/sources.json'
sources_with_ids = 'har/__sr/har/sources.json'
created_sources = 'har/__sr/har/sources.json'

# Beautify XML
#helpers.beautify_xml(file_path, prettified_file)

# Transform XML to JSON
#parse_har_concepts.parse_xml(prettified_file, output_json)

# Import sources and append their IDs to source data file

import_sources.assign_ids_to_all_sources(sources_without_ids, sources_with_ids, created_sources)

# Append source IDs to sourcelinks

# Check for words and append their IDs to words in concepts JSON

for handler in logger.handlers[:]:
    handler.close()
    logger.removeHandler(handler)
