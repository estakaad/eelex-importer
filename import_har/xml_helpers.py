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


def map_lang_codes_to_names(lang_code_xml):
    codes = {
        "hisp": "hispaania",
        "ingl": "inglise",
        "kr": "kreeka",
        "ld": "ladina",
        "pr": "prantsuse",
        "sks": "saksa"
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


def write_dicts_to_json_file(dicts_list, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        dicts_to_serialize = [asdict(obj) for obj in dicts_list]
        json.dump(dicts_to_serialize, f, ensure_ascii=False, indent=4)


def replace_guids_with_meaning_ids(json_with_guids_path, json_with_mappings_path, output_path):
    with open(json_with_guids_path, 'r', encoding='utf-8') as file:
        data_with_guids = json.load(file)

    with open(json_with_mappings_path, 'r', encoding='utf-8') as file:
        mappings = json.load(file)

    guid_to_id_map = {item["conceptIds"][0]: item["id"] for item in mappings}

    for item in data_with_guids:
        if item["meaningId"] in guid_to_id_map:
            item["meaningId"] = guid_to_id_map[item["meaningId"]]

        if item["targetMeaningId"] in guid_to_id_map:
            item["targetMeaningId"] = guid_to_id_map[item["targetMeaningId"]]

    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(data_with_guids, file, ensure_ascii=False, indent=4)