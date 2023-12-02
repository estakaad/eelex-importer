from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
import data_classes
import parse_xml
import xml_helpers

input_xml_file_path = "har/__sr/har/beautified_har.xml"
output_json_file_path = 'har/__sr/har/har.json'

concepts = parse_xml.parse_xml(input_xml_file_path)

xml_helpers.write_dicts_to_json_file(concepts, output_json_file_path)