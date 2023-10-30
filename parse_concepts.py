from xml.dom.minidom import parse
import xml.etree.ElementTree as ET
import json

def beautify_xml(file_path, prettified_file):

    dom = parse(file_path)

    pretty_xml_str = dom.toprettyxml(indent="  ")

    with open(prettified_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_str)


def parse_domains(A):
    domains = A.findall(".//x:po", namespaces={"x": "http://www.eki.ee/dict/teo"})
    domain_list = [{"code": d.text} for d in domains if d.text]
    return domain_list

def parse_definitions(S):
    definitions = []
    definition = S.find(".//x:def", namespaces={"x": "http://www.eki.ee/dict/teo"})
    if definition is not None:
        definitions.append({
            "value": definition.text,
            "lang": "est",
            "definitionTypeCode": "definitsioon",
            "sourceLinks": []
        })
    return definitions

def parse_words(P):
    words = []
    for ter in P.findall(".//x:ter", namespaces={"x": "http://www.eki.ee/dict/teo"}):
        words.append({
            "value": ter.text,
            "lang": ter.attrib.get("x:tyyp", ""),
            "wordTypeCodes": []
        })
    return words

def parse_entry(A):
    entry = {}

    # Parse domains
    entry["domains"] = parse_domains(A)

    # Parse P element for words
    P = A.find(".//x:P", namespaces={"x": "http://www.eki.ee/dict/teo"})
    if P is not None:
        entry["words"] = parse_words(P)

    # Parse S element for definitions
    S = A.find(".//x:S", namespaces={"x": "http://www.eki.ee/dict/teo"})
    if S is not None:
        entry["definitions"] = parse_definitions(S)

    return entry

def parse_xml(input_filename, output_filename):
    tree = ET.parse(input_filename)
    root = tree.getroot()

    entries = []

    for A in root.findall(".//x:A", namespaces={"x": "http://www.eki.ee/dict/teo"}):
        entry = parse_entry(A)
        entries.append(entry)

    json_output = json.dumps(entries, indent=4, ensure_ascii=False)

    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(json_output)