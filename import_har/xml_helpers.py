from dataclasses import asdict
import xml.etree.ElementTree as ET
import json


def map_lang_codes(lang_code_xml):
    codes = {
        "et": "est",
        "ru": "rus",
        "ee": "est",
        "en": "eng",
        "de": "deu",
        "fi": "fin"
    }

    return codes.get(lang_code_xml, "unknown")


# Dictionary, milles on GUIDid ja keelendid. Vajalik seoste loomiseks.
def build_guid_word_dict(file_path):
    ns = {
        'h': 'http://www.eki.ee/dict/har',
        'xml': 'http://www.w3.org/XML/1998/namespace'
    }

    tree = ET.parse(file_path)
    root = tree.getroot()

    guid_word_dict = {}

    for a_element in root.findall('.//h:A', ns):
        guid_element = a_element.find('.//h:G', ns)
        if guid_element is not None:
            guid = guid_element.text
            for ter_element in a_element.findall('.//h:ter', ns):
                term = ter_element.text
                if term:
                    guid_word_dict[term] = guid

    return guid_word_dict


# Otsi GUID keelendi järgi. Vajalik seoste loomiseks.
def find_guid_by_term(term, guid_word_dict):

    if guid_word_dict.get(term):
        return guid_word_dict.get(term)
    else:
        return None


