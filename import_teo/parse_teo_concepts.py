from xml.dom.minidom import parse
import xml.etree.ElementTree as ET
import json


def parse_domains(A):
    domains = A.findall(".//x:v", namespaces={"x": "http://www.eki.ee/dict/teo"})
    domain_list = [{"code": d.text,
                    "origin": None
                    } for d in domains if d.text]
    return domain_list


def parse_notes(A):
    notes_list = []

    for dg in A.findall(".//x:dg", namespaces={"x": "http://www.eki.ee/dict/teo"}):
        lisa = dg.find(".//x:lisa", namespaces={"x": "http://www.eki.ee/dict/teo"})
        all_element = dg.find(".//x:all", namespaces={"x": "http://www.eki.ee/dict/teo"})

        sourceLinks = []
        if all_element is not None:
            sourceLinks.append({"value": all_element.text, "name": ""})

        if lisa is not None and lisa.text:
            notes_list.append({
                "value": lisa.text,
                "lang": "est",
                "publicity": True,
                "sourceLinks": sourceLinks
            })

    confession = A.findall(".//x:konf", namespaces={"x": "http://www.eki.ee/dict/teo"})
    for c in confession:
        notes_list.append({
            "value": c.text,
            "lang": "est",
            "publicity": True,
            "sourceLinks": []
        })

    author = A.find(".//x:T", namespaces={"x": "http://www.eki.ee/dict/teo"})
    notes_list.append({
        "value": author.text,
        "lang": "est",
        "publicity": False,
        "sourceLinks": []
    })

    return notes_list


def parse_definitions(S):
    definitions = []
    definition = S.find(".//x:def", namespaces={"x": "http://www.eki.ee/dict/teo"})
    if definition is not None:
        definitions.append({
            "value": definition.text,
            "lang": "est",
            "definitionTypeCode": "definitsioon",
            "sourceLinks": []
        })
    return definitions


def parse_usage(S):
    usages = []
    for ng in S.findall(".//x:ng", namespaces={"x": "http://www.eki.ee/dict/teo"}):
        n_element = ng.find(".//x:n", namespaces={"x": "http://www.eki.ee/dict/teo"})
        nall_element = ng.find(".//x:nall", namespaces={"x": "http://www.eki.ee/dict/teo"})

        sourceLinks = []
        if nall_element is not None:
            sourceLinks.append({"value": nall_element.text, "name": ""})

        if n_element is not None:
            usages.append({
                "value": n_element.text,
                "lang": "est",
                "sourceLinks": sourceLinks
            })

    return usages


def parse_words(P, A):
    words = []

    for terg in P.findall(".//x:terg", namespaces={"x": "http://www.eki.ee/dict/teo"}):
        ter = terg.find(".//x:ter", namespaces={"x": "http://www.eki.ee/dict/teo"})
        tall = terg.find(".//x:tall", namespaces={"x": "http://www.eki.ee/dict/teo"})
        etym = terg.find(".//x:etym", namespaces={"x": "http://www.eki.ee/dict/teo"})

        lexemeValueStateCode = ter.attrib.get('{http://www.eki.ee/dict/teo}tyyp', '')
        if lexemeValueStateCode == 'ee':
            lexemeValueStateCode = 'eelistermin'
        else:
            lexemeValueStateCode = None

        sourceLinks = []
        if tall is not None:
            sourceLinks.append(
                {
                    "sourceId": None,
                    "value": tall.text,
                    "name": None
                })

        words.append({
            "value": ter.text,
            "lang": etym.text if etym is not None else None,
            "lexemeValueStateCode": [lexemeValueStateCode] if lexemeValueStateCode else None,
            "sourceLinks": sourceLinks
        })

    for xp in A.findall(".//x:xp", namespaces={"x": "http://www.eki.ee/dict/teo"}):
        lang = xp.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', '')
        for x in xp.findall(".//x:x", namespaces={"x": "http://www.eki.ee/dict/teo"}):
            words.append({
                "value": x.text,
                "lang": lang,
                "wordTypeCodes": [],
                "sourceLinks": []
            })

    return words


def parse_concept_ids(A):
    c_id = A.find(".//x:G", namespaces={"x": "http://www.eki.ee/dict/teo"})
    c_ids = []
    c_ids.append(c_id.text)
    return c_ids


def parse_forums(A):
    forums = []
    for komg in A.findall(".//x:komg", namespaces={"x": "http://www.eki.ee/dict/teo"}):
        kom_element = komg.find(".//x:kom", namespaces={"x": "http://www.eki.ee/dict/teo"})
        kaut_element = komg.find(".//x:kaut", namespaces={"x": "http://www.eki.ee/dict/teo"})

        forum_value = ""

        if kom_element is not None:
            forum_value += kom_element.text

        if kaut_element is not None:
            forum_value += " - " + kaut_element.text

        if forum_value:
            forums.append({"value": forum_value})

    return forums


def parse_entry(A):
    entry = {}

    # Parse domains
    entry["domains"] = parse_domains(A)

    entry["notes"] = parse_notes(A)

    entry["usages"] = parse_usage(A)

    entry["forums"] = parse_forums(A)

    # Parse P element for words
    P = A.find(".//x:P", namespaces={"x": "http://www.eki.ee/dict/teo"})
    if P is not None:
        entry["words"] = parse_words(P, A)

    # Parse S element for definitions
    S = A.find(".//x:S", namespaces={"x": "http://www.eki.ee/dict/teo"})
    if S is not None:
        entry["definitions"] = parse_definitions(S)

    entry["conceptIds"] = parse_concept_ids(A)

    return entry

def parse_xml(input_filename, output_filename):
    tree = ET.parse(input_filename)
    root = tree.getroot()

    entries = []

    for A in root.findall(".//x:A", namespaces={"x": "http://www.eki.ee/dict/teo"}):
        entry = parse_entry(A)
        entries.append(entry)

    json_output = json.dumps(entries, indent=4, ensure_ascii=False)

    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(json_output)