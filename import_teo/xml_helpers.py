from dataclasses import asdict
import json


def normalize_text(input_text):
    if input_text is None:
        return ''
    return input_text.replace('\\"', '"').replace('\\', '').replace('  ', ' ')


def get_source_id_by_name(name, sources_with_ids):
    normalized_name = normalize_text(name)

    start_index_of_lk = normalized_name.find('lk ')
    start_index_of_par = normalized_name.find(' par ')

    if start_index_of_lk != -1:
        inner_name = normalized_name[start_index_of_lk:].strip(' ').strip('.')
        #print(normalized_name + ' - ' + inner_name)
    elif start_index_of_par != -1:
        inner_name = normalized_name[start_index_of_par:].strip(' ').strip('.')
        #print(normalized_name + ' - ' + inner_name)
    elif 'KKK, ' in normalized_name:
        inner_name = normalized_name.replace('KKK, ', '')
        #print(normalized_name + ' - ' + inner_name)
    elif 'KKK kompendium, ' in normalized_name:
        inner_name = normalized_name.replace('KKK kompendium, ', '')
        #print(normalized_name + ' - ' + inner_name)
    elif 'XXII pt' in normalized_name:
        inner_name = '22. ptk'
        #print(normalized_name + ' - ' + inner_name)
    else:
        inner_name = ''

    sources = {
        "EVÕSS": 16733,
        "Salumaa 2008": 22637,
        "Wikipedia": 19621,
        "Britannica": 19250,
        "EKRL": 16734,
        "SPL": 16679,
        "VL": 22967,
        "Salo 2000": 22611,
        "TEA": 22698,
        "HarperCollins": 22622,
        "LThK 1993": 22663,
        "New Advent": 22621,
        "ПЭ": 22973,
        "EncChr": 22918,
        "Riistan 2011": 22969,
        "Blackwell": 22970,
        "Day": 22971,
        "BibleGateway": 22972,
        "BERTA": 19301,
        "Grenz": 22974,
        "CARM": 22975,
        "EKSS": None
    }

    if normalized_name in sources:
        source_id = sources[normalized_name]
    else:
        source_id = next((item['sourceId'] for item in sources_with_ids if normalize_text(item['allikaviide_eelexis']) == normalized_name), 63838)

    return int(source_id) if source_id is not None else None, str(inner_name)


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
        "tl": "tgl"
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


def map_domain_to_lenoch_code(domain):
    names = {
        "dogmaatika": "RP51",
        "filosoofia": "RP",
        "kirikuarhitektuur": "RP72",
        "kirikukorraldus": "RP23",
        "kirikulugu": "RPD",
        "kirikumuusika": "RPC1",
        "kirikuõigus": "RPJ",
        "kristlik kunst": "RP71",
        "liturgika": "RPC2",
        "piibliteadus": "RP6",
        "religioonisotsioloogia": "RPE1",
        "teoloogia": "RP5",
        "kristoloogia": "RP52",
        "anglikaani": "RP94",
        "baptisti": "RP97",
        "katoliku": "RP93",
        "luteri": "RP95",
        "reformeeritud": "RP96",
        "vanaida": "RP92",
        "õigeusu": "RP92"
    }

    return names.get(domain, "unknown")


def find_guid_for_words(concepts, relation_links):
    relation_links_with_all_guids = []
    for rl in relation_links:
        for c in concepts:
            for w in c.words:
                if rl[1] == w.valuePrese:
                    relation_links_with_all_guids.append((rl[0], c.conceptIds[0]))

    return relation_links_with_all_guids


def write_dicts_to_json_file(dicts_list, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        dicts_to_serialize = [asdict(obj) for obj in dicts_list]
        json.dump(dicts_to_serialize, f, ensure_ascii=False, indent=4)