from datetime import datetime
import json
from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
import data_classes
import xml_helpers
import re
import csv
import sources_helpers
import parse_tg
import parse_xp
import parse_terg


ns = {
    'h': 'http://www.eki.ee/dict/har',
    'xml': 'http://www.w3.org/XML/1998/namespace'
}


# XMLi parsimine, mõistete objektide kokkupanek
def parse_xml(dataset_code, file_path, sources_file_path):

    guid_word_dict = xml_helpers.build_guid_word_dict(file_path)

    sources_with_ids = sources_helpers.load_sources(sources_file_path)

    tree = ET.parse(file_path)
    root = tree.getroot()

    concepts = []
    sources = []

    all_relations = []

    for a_element in root.findall('.//h:A', ns):
        domains = []
        conceptids = []
        manualEventOn = None
        manualEventBy = None
        firstCreateEventOn = None
        firstCreateEventBy = None
        notes = []
        forums = []
        definitions = []
        words = []

        # Valdkonnad
        for v_element in a_element.findall('.//h:v', ns):
            d_domain = v_element.text
            d_origin = 'har'
            domain = {
                'code': d_domain,
                'origin': d_origin
            }
            domains.append(domain)

        # GUID
        for guid in a_element.findall('.//h:G', ns):
            conceptids.append(guid.text)

        # Koostamisaeg - createdAt
        for created_at in a_element.findall('.//h:KA', ns):
            firstCreateEventOn = created_at.text
            dt = datetime.strptime(firstCreateEventOn, "%Y-%m-%dT%H:%M:%S")
            firstCreateEventOn = dt.strftime("%d.%m.%Y")

        # Koostaja - creator
        for creator in a_element.findall('.//h:K', ns):
            firstCreateEventBy = creator.text

        # Viimane muutja
        for editor in a_element.findall('.//h:T', ns):
            manualEventBy = editor.text

        # Mõiste tähendusgrupp
        for tg_element in a_element.findall('.//h:tg', ns):
            definition, notes_from_xml, forums_from_xml, sources_from_xml, seotud_relations = \
                parse_tg.tg_def_definition(tg_element, sources_with_ids, conceptids, guid_word_dict, ns)

            if definition:
                definitions.append(definition)
            for note in notes_from_xml:
                if note.value:
                    notes.append(note)
            for forum in forums_from_xml:
                if forum.value:
                    forums.append(forum)
            for s in sources_from_xml:
                sources.append(s)

            if len(seotud_relations) > 0:
                for sr in seotud_relations:
                    all_relations.append(sr)

        # Kommentaarid

        for kom_group_element in a_element.findall('.//h:komg', ns):
            for kom_elem in kom_group_element.findall('.//h:kom', ns):
                content = kom_elem.text
            for kom_aut_elem in kom_group_element.findall('.//h:kaut', ns):
                author = kom_aut_elem.text
            for kom_t_elem in kom_group_element.findall('.//h:kaeg', ns):
                time = kom_t_elem.text

            notes.append(
                data_classes.Note(
                    value=content + ' (' + author + ', ' + time + ')',
                    lang='est',
                    publicity=False,
                    sourceLinks=[]
                )
            )

        words_from_est_terms, concept_notes = parse_terg.ter_word(sources_with_ids, a_element, ns)

        # Eestikeelsed terminid
        for w in words_from_est_terms:
            words.append(w)

        for c in concept_notes:
            notes.append(c)

        # Võõrkeelsed vasted

        foreign_words, foreign_definitions, sources_from_xp = parse_xp.xp_to_words(a_element, sources_with_ids, ns)

        for w in foreign_words:
            if w.valuePrese:
                words.append(w)

        for d in foreign_definitions:
            if d.value:
                definitions.append(d)

        for s in sources_from_xp:
            sources.append(s)


        # Koosta mõiste objekt
        concept = data_classes.Concept(
            datasetCode=dataset_code,
            conceptIds=conceptids,
            domains=domains,
            manualEventOn=manualEventOn,
            manualEventBy=manualEventBy,
            firstCreateEventOn=firstCreateEventOn,
            firstCreateEventBy=firstCreateEventBy,
            definitions=definitions,
            notes=notes,
            forums=forums,
            words=words
        )

        if not a_element.findall('.//h:KL', ns):
            for n in concept.notes:
                n.publicity = False
            for w in concept.words:
                w.lexemePublicity = False
                for ln in w.lexemeNotes:
                    ln.publicity = False
                for u in w.usages:
                    u.publicity = False

        # HTML märgendus
        for d in concept.definitions:
            d.value = d.value.replace('&ema;','<eki-foreign>').replace('&eml;','</eki-foreign>')
        for n in concept.notes:
            n.value = n.value.replace('&ema;','<eki-foreign>').replace('&eml;','</eki-foreign>')
        for w in concept.words:
            w.valuePrese = w.valuePrese.replace('&ema;','<eki-foreign>').replace('&eml;','</eki-foreign>')
            for ln in w.lexemeNotes:
                ln.value = ln.value.replace('&ema;','<eki-foreign>').replace('&eml;','</eki-foreign>')
            for u in w.usages:
                u.value = u.value.replace('&ema;','<eki-foreign>').replace('&eml;','</eki-foreign>')

        concepts.append(concept)

    relations_list_json = []

    for item in all_relations:
        parts = item.strip().split('; ')

        if parts[1] == 'seotud':
            relationTypeCode = 'seotud mõiste'
            oppositeRelationTypeCode = 'seotud mõiste'

            json_object = {
                "meaningId": parts[0],
                "targetMeaningId": parts[2],
                "relationTypeCode": relationTypeCode,
                "oppositeRelationTypeCode": oppositeRelationTypeCode
            }

            relations_list_json.append(json_object)
        elif parts[1] == 'antonüüm':
            relationTypeCode = 'antonüüm'
            oppositeRelationTypeCode = 'antonüüm'

            json_object = {
                "meaningId": parts[0],
                "targetMeaningId": parts[2],
                "relationTypeCode": relationTypeCode,
                "oppositeRelationTypeCode": oppositeRelationTypeCode
            }

            relations_list_json.append(json_object)
        else:
            print('error - vigane seos - ' + item)
            continue

    with open('seosed.json', 'w', encoding='utf-8') as json_file:
        json.dump(relations_list_json, json_file, ensure_ascii=False, indent=4)

    return concepts