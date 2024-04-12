import xml_helpers

# Open file concepts_saved.json
# Check: are there lexeme notes with comment "Grammatiline sugu" and there is wordId?

file_path_concepts_saved = 'files/concepts_saved.json'
saved_concepts = xml_helpers.load_json_data(file_path_concepts_saved)

map_genders = {
    'm': 'm',
    'ж': 'f',
    'м': 'm',
    'f': 'f',
    'n': 'n',
    'с': 'n'
}

list = ['lexemeid', 'gr gender']

for c in saved_concepts:
    for w in c['words']:
        if 'valuePrese' in w:
            for note in w['lexemeNotes']:
                if 'value' in note:
                    if note['value'].startswith('Grammatiline sugu'):
                        #print(c['id'])
                        print(note['value'])

# Create a list of meaning IDs

# GET all meanings by ID

# If