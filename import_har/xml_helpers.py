from dataclasses import asdict
import json

def get_source_id_by_name(name):
    sources = {
    "PGS": 1,
    "Bloom": 2,
    "PED-TERM": 3,
    "TESE": 4,
    "ISO": 5,
    "Kraav": 6,
    "Hirsjärvi": 7,
    "EKSS": 8,
    "ÕS": 9,
    "akad. kraadid": 10,
    "rmt-kogu": 11,
    "VL 2006": 12,
    "HP": 13,
    "Vallaste": 14,
    "Smith": 15,
    "Laanemäe": 16,
    "TEST": 17,
    "AKS": 18,
    "ÕK": 19,
    "ANDR": 20,
    "Krull": 21,
    "HTS": 22,
    "Koort": 23,
    "Dict of Psychol": 24,
    "Vääri": 25,
    "VL": 26,
    "E(N)E": 27,
    "Erelt": 28,
    "Koemets": 29,
    "Raili Pool": 30,
    "Good ja Power": 31,
    "ERIP": 32,
    "Ekspert": 33
}
    #return sources.get(name, "Unknown Source")
    return 121611

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

def write_dicts_to_json_file(dicts_list, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        dicts_to_serialize = [asdict(obj) for obj in dicts_list]
        json.dump(dicts_to_serialize, f, ensure_ascii=False, indent=4)

def get_source_name_from_source(source):
    if 'wikipedia' in source:
        return 'Wikipedia'
    elif source.startswith('https'):
        split_https = source.split('https://')[-1]
        split_dot = split_https.split('.')[0]
        name = split_dot.replace('www.', '') if 'www.' in split_dot else split_dot
        return name
    elif source.startswith('http'):
        split_https = source.split('http://')[-1]
        split_dot = split_https.split('.')[0]
        name = split_dot.replace('www.', '') if 'www.' in split_dot else split_dot
        return name
    else:
        return source

def load_sources(path):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_source_id_by_source_text(data, source_text):
    for entry in data:
        if entry.get('valuePrese') == source_text:
            #print(source_text)
            return entry.get('id')
        else:
            continue