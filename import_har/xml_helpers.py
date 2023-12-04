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
    "ERIP": 32
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
