# CONCEPT

from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
import data_classes
import xml_helpers
from datetime import datetime
import ter_word_parse
import xp_parse
import tg_parse

ns = {
    'x': 'http://www.eki.ee/dict/has',
    'xml': 'http://www.w3.org/XML/1998/namespace'
}

def parse_xml(file_path, sources_with_ids):
    tree = ET.parse(file_path)
    root = tree.getroot()

    concepts = []
    relations_with_one_guid = []

    for a_element in root.findall('.//x:A', ns):
        if a_element.attrib.get(f'{{{ns["x"]}}}as', '') == 'elx':
            continue
        else:
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
            for v_element in a_element.findall('.//x:v', ns):
                d_domain = v_element.text
                d_origin = 'has'
                domain = {
                    'code': d_domain,
                    'origin': d_origin
                }
                domains.append(domain)

            # GUID
            for guid in a_element.findall('.//x:G', ns):
                conceptids.append(guid.text)

            # Koostamise algus
            for ka in a_element.findall('.//x:KA', ns):
                dt = datetime.strptime(ka.text, "%Y-%m-%dT%H:%M:%S")
                firstCreateEventOn = dt.strftime("%d.%m.%Y %H:%M")

            # Toimetaja
            for editor in a_element.findall('.//x:T', ns):
                if editor.text == 'ETamm':
                    value = 'Eva Tamm'
                else:
                    value = editor.text

                notes.append(data_classes.Note(
                    value='Artikli toimetaja: ' + value,
                    lang='est',
                    publicity=False,
                    sourceLinks=[]
                ))

            # Definitsioonid, märkused, sisemärkused
            for tg_element in a_element.findall('.//x:tg', ns):
                definition, notes_from_xml, forums_from_xml, relations_without_guids = tg_parse.tg_def_definition(tg_element, sources_with_ids)

                if definition:
                    definitions.append(definition)

                for note in notes_from_xml:
                    if note.value:
                        notes.append(note)
                for forum in forums_from_xml:
                    if forum.value:
                        forums.append(forum)

                modified_relations = [conceptids[0] + '; ' + r for r in relations_without_guids]

                for m in modified_relations:
                    relations_with_one_guid.append(m)

            # Kommentaarid (sisemärkusteks)
            for kom_group_element in a_element.findall('.//x:komg', ns):
                for kom_elem in kom_group_element.findall('.//x:kom', ns):
                    content = kom_elem.text
                for kom_aut_elem in kom_group_element.findall('.//x:kaut', ns):
                    author = kom_aut_elem.text

                forum_item = data_classes.Forum(
                    value=content.replace('&ema;', '<eki-foreign>').replace('&eml;', '</eki-foreign>').
                          replace('&ba;', '<eki-highlight>').replace('&bl;', '</eki-highlight>') + ' (' + author + ')'
                )

                forums.append(forum_item)

            # Eestikeelsed terminid
            for w in ter_word_parse.ter_word(a_element, sources_with_ids):
                words.append(w)

            # Võõrkeelsed terminid
            foreign_words, foreign_definitions = xp_parse.xp_to_words(a_element, sources_with_ids)

            for w in foreign_words:
                if w.valuePrese:
                    words.append(w)

            for d in foreign_definitions:
                if d.value:
                    definitions.append(d)


            concept = data_classes.Concept(
                datasetCode='has-02-05',
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

            concepts.append(concept)

    return concepts, relations_with_one_guid

