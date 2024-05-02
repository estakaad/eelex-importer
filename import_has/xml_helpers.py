from dataclasses import asdict
import json


def map_lang_codes(lang_code_xml):
    codes = {
        "et": "est",
        "ru": "rus",
        "ee": "est",
        "en": "eng",
        "de": "deu",
        "fi": "fin",
        "fr": "fra",
        "ld": "lat",
        "kr": "ell",
        "vkr": "grc",
        "rts": "swe",
        "le": "lit",
        "hbr": "heb",
        "pl": "pol",
        "lt": "lav",
        "it": "ita",
        "tl": "tgl",
        "pr": "fra",
        "ingl": "eng"
    }

    return codes.get(lang_code_xml, "unknown")

def map_lang_acronyms(code):
    codes = {
        "sks": "saksa",
        "ld": "ladina",
        "kr": "kreeka",
        "vkr": "vanakreeka",
        "rts": "rootsi",
        "le": "leedu",
        "hbr": "heebrea",
        "it": "itaalia",
        "ingl": "inglise",
        "hisp": "hispaania",
        "pl": "poola",
        "tl": "tagalogi"
    }

    return codes.get(code, "unknown")

def write_dicts_to_json_file(dicts_list, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        dicts_to_serialize = [asdict(obj) for obj in dicts_list]
        json.dump(dicts_to_serialize, f, ensure_ascii=False, indent=4)



# Allikate laadimine dictionaryde listina
def load_sources(path):
    with open(path, 'r', encoding='utf-8') as file:
        sources = json.load(file)
        return sources


# Otsib allika ID ja lühikese kuju XMLis oleva pika kuju järgi
def get_source_id_and_name_by_source_text(data, source_text):

    inner_link = ''

    for entry in data:
        if entry.get('value') == source_text:
            return entry.get('test_id'), entry.get('name'), entry.get('siseviide')
        else:
            continue

    print('Ei leidnud allikat: ' + source_text)

    return 0, 'unknown', inner_link


def get_second_guid_by_term(relations, concepts):

    relations_with_guids = []

    for r in relations:
        parts = r.split(';')
        term = parts[-1].strip()
        meaning_id = parts[0]
        relation_type = parts[1]

        for c in concepts:
            for w in c.words:
                if w.valuePrese == term:
                    relation_object = {
                        "meaningId": meaning_id,
                        "targetMeaningId": c.conceptIds[0],
                        "relationTypeCode": relation_type,
                        "oppositeRelationTypeCode": relation_type
                    }
                    relations_with_guids.append(relation_object)

    return relations_with_guids


def replace_guids_with_meaning_ids(json_with_guids, json_with_mappings_path, output_path):

    with open(json_with_mappings_path, 'r', encoding='utf-8') as file:
        mappings = json.load(file)

    guid_to_id_map = {item["conceptIds"][0]: item["id"] for item in mappings}

    for item in json_with_guids:
        if item["meaningId"] in guid_to_id_map:
            item["meaningId"] = guid_to_id_map[item["meaningId"]]

        if item["targetMeaningId"] in guid_to_id_map:
            item["targetMeaningId"] = guid_to_id_map[item["targetMeaningId"]]

    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(json_with_guids, file, ensure_ascii=False, indent=4)