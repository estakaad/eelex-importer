from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
import data_classes
import parse_xml

file_path = "har/__sr/har/beautified_har.xml"
concepts = parse_xml.parse_xml(file_path)

for concept in concepts:
    print(concept)