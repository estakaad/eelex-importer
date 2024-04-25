import json


# Allikate lühikese kuju paremaks tegemiseks
def sanitise_sources_file(path, new_path):
    with open(path, 'r', encoding='utf-8') as file:
        sources = json.load(file)

        for s in sources:
            if 'wiki' in s['name']:
                s['name'] = 'Wikipedia'
            elif 'EKSPERT' in s['name']:
                s['public'] = False
                s['name'] = 'Ekspert'
            elif s['name'].startswith('https'):
                parts = s['name'].split('https://')
                new_parts = parts[1].split('/')
                s['name'] = new_parts[0]
                s['name'] = s['name'].replace('www.', '')
                s['name'] = s['name'].strip('/')
            elif s['name'].startswith('http'):
                s['name'].strip('http://')
                parts = s['name'].split('/')
                s['name'] = parts[2].replace('www.', '')
            else:
                continue

    with open(new_path, 'w', encoding='utf-8') as file:
        json.dump(sources, file, ensure_ascii=False, indent=4)


# Allikate laadimine dictionaryde listina
def load_sources(path):
    with open(path, 'r', encoding='utf-8') as file:
        sources = json.load(file)
        return sources


# Otsib allika ID ja lühikese kuju XMLis oleva pika kuju järgi
def get_source_id_and_name_by_source_text(data, source_text):
    if 'Veldi' in source_text:
        source_text = 'Veldi'

    inner_link = ''

    if 'lk ' in source_text:
        parts = source_text.split('lk ')
        source_text = parts[0].strip().strip('.')
        inner_link = 'lk ' + parts[1]

    for entry in data:
        if entry.get('valuePrese') == source_text:
            return entry.get('id'), entry.get('name'), inner_link
        else:
            continue

    print('Ei leidnud allikat: ' + source_text)

    return 0, 'unknown', inner_link