import pandas as pd
import json

excel_path = 'allikad_uute_id_deta.xlsx'
data = pd.read_excel(excel_path)

json_path = 'sources_with_ids.json'
with open(json_path, 'r', encoding='utf-8') as file:
    json_data = json.load(file)

id_map = {(str(item['name']).strip(), str(item['valuePrese']).strip()): item['id'] for item in json_data}

def update_sourceid(row):
    if pd.isna(row['sourceId']):
        name = str(row['name']).strip()
        value_prese = str(row['valuePrese']).strip()
        key = (name, value_prese)
        if key not in id_map:
            print(f"ERROR: No match found for ({name}, {value_prese})")
        return id_map.get(key, None)
    return int(row['sourceId'])

data['sourceId'] = data.apply(update_sourceid, axis=1)

output_path = 'allikad_uute_id_dega.json'
data.to_json(output_path, orient='records', lines=True, force_ascii=False)