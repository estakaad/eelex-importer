import xml.etree.ElementTree as ET
from xml.dom.minidom import parse

def beautify_xml(file_path, prettified_file):

    dom = parse(file_path)

    pretty_xml_str = dom.toprettyxml(indent="  ")

    with open(prettified_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_str)


def match_language(lang):
    if lang == "ee":
        return "est"
    elif lang == "hisp":
        return "spa"
    elif lang == "ingl":
        return "eng"
    elif lang == "it":
        return "ita"
    elif lang == "kr":
        return "ell"
    elif lang == "ld":
        return "lat"
    elif lang == "pr":
        return "fra"
    elif lang == "sks":
        return "deu"
    elif lang == "sm":
        return "fin"
    elif lang == "vkr":
        return ""
    elif lang == "vn":
        return "rus"
    elif lang == "fi":
        return "fin"
    elif lang == "de":
        return "deu"
    elif lang == "en":
        return "eng"
    elif lang == "ru":
        return "rus"
    else:
        return None
