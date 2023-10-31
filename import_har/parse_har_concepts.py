from xml.dom.minidom import parse
import xml.etree.ElementTree as ET
import json
import helpers


def parse_domains(A):
    domains = A.findall(".//h:v", namespaces={"h": "http://www.eki.ee/dict/har"})
    domain_list = [{"code": d.text,
                    "origin": None
                    } for d in domains if d.text]
    return domain_list


# def parse_notes(A):
#     notes_list = []
#
#     for dg in A.findall(".//h:dg", namespaces={"h": "http://www.eki.ee/dict/har"}):
#         lisa = dg.find(".//h:lisa", namespaces={"h": "http://www.eki.ee/dict/har"})
#         all_element = dg.find(".//h:all", namespaces={"h": "http://www.eki.ee/dict/har"})
#
#         sourceLinks = []
#         if all_element is not None:
#             sourceLinks.append({"value": all_element.text, "name": ""})
#
#         if lisa is not None and lisa.text:
#             notes_list.append({
#                 "value": lisa.text,
#                 "lang": "est",
#                 "publicity": True,
#                 "sourceLinks": sourceLinks
#             })
#
#     confession = A.findall(".//h:konf", namespaces={"h": "http://www.eki.ee/dict/har"})
#     for c in confession:
#         notes_list.append({
#             "value": c.text,
#             "lang": "est",
#             "publicity": True,
#             "sourceLinks": []
#         })
#
#     author = A.find(".//h:T", namespaces={"h": "http://www.eki.ee/dict/har"})
#     notes_list.append({
#         "value": author.text,
#         "lang": "est",
#         "publicity": False,
#         "sourceLinks": []
#     })
#
#     return notes_list


# OK
def parse_definitions(S):
    definitions = []
    for dg in S.findall(".//h:dg", namespaces={"h": "http://www.eki.ee/dict/har"}):
        definition = dg.find(".//h:def", namespaces={"h": "http://www.eki.ee/dict/har"})
        all_element = dg.find(".//h:all", namespaces={"h": "http://www.eki.ee/dict/har"})

        sourceLinks = []
        if all_element is not None:
            sourceLinks.append({"value": all_element.text, "name": ""})

        if definition is not None:
            definitions.append({
                "value": definition.text,
                "lang": "est",
                "definitionTypeCode": "definitsioon",
                "sourceLinks": sourceLinks
            })
    return definitions


# def parse_usage(S):
#     usages = []
#     for ng in S.findall(".//h:ng", namespaces={"h": "http://www.eki.ee/dict/har"}):
#         n_element = ng.find(".//h:n", namespaces={"h": "http://www.eki.ee/dict/har"})
#         nall_element = ng.find(".//h:nall", namespaces={"h": "http://www.eki.ee/dict/har"})
#
#         sourceLinks = []
#         if nall_element is not None:
#             sourceLinks.append({"value": nall_element.text, "name": ""})
#
#         if n_element is not None:
#             usages.append({
#                 "value": n_element.text,
#                 "lang": "est",
#                 "sourceLinks": sourceLinks
#             })
#
#     return usages


# valueStateCode - OK

def parse_words(P, A):
    words = []

    for terg in P.findall(".//h:terg", namespaces={"h": "http://www.eki.ee/dict/har"}):
        ter = terg.find(".//h:ter", namespaces={"h": "http://www.eki.ee/dict/har"})
        tall = terg.find(".//h:tall", namespaces={"h": "http://www.eki.ee/dict/har"})
        etym = terg.find(".//h:etym", namespaces={"h": "http://www.eki.ee/dict/har"})

        lang = ''
        if etym:
            lang = helpers.match_language(etym.text)

        lexemeValueStateCode = ter.attrib.get('{http://www.eki.ee/dict/har}tyyp', '')
        if lexemeValueStateCode == 'ee':
            lexemeValueStateCode = 'eelistermin'

        # Set language to 'est' if lexemeValueStateCode is 'eelistermin' and lang is empty
        if lexemeValueStateCode == 'eelistermin' and not lang:
            lang = "est"

        sourceLinks = []
        if tall is not None:
            sourceLinks.append({
                "sourceId": None,
                "value": tall.text,
                "name": None
            })

        words.append({
            "value": ter.text,
            "lang": lang if lang is not None else "",
            "lexemeValueStateCode": [lexemeValueStateCode] if lexemeValueStateCode else None,
            "sourceLinks": sourceLinks
        })

    for xp in A.findall(".//h:xp", namespaces={"h": "http://www.eki.ee/dict/har"}):
            lang = xp.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', '')
            if lang:
                lang = helpers.match_language(lang)  # Assuming match_language function is defined or imported
            for x in xp.findall(".//h:x", namespaces={"h": "http://www.eki.ee/dict/har"}):
                lexemeValueStateCode = []
                tyyp = x.attrib.get('{http://www.eki.ee/dict/har}tyyp', '')
                if tyyp == 'ee':
                    lexemeValueStateCode.append("eelistermin")

                # Set language to 'est' if lexemeValueStateCode is 'eelistermin' and lang is empty
                if 'eelistermin' in lexemeValueStateCode and not lang:
                    lang = "est"

                words.append({
                    "value": x.text,
                    "lang": lang if lang is not None else "",
                    "lexemeValueStateCode": lexemeValueStateCode if lexemeValueStateCode else None,
                    "sourceLinks": []
                })

    return words


def parse_concept_ids(A):
    c_id = A.find(".//h:G", namespaces={"h": "http://www.eki.ee/dict/har"})
    c_ids = []
    c_ids.append(c_id.text)
    return c_ids


def parse_forums(A):
    forums = []
    for komg in A.findall(".//h:komg", namespaces={"h": "http://www.eki.ee/dict/har"}):
        kom_element = komg.find(".//h:kom", namespaces={"h": "http://www.eki.ee/dict/har"})
        kaut_element = komg.find(".//h:kaut", namespaces={"h": "http://www.eki.ee/dict/har"})

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

    # Parse domains - OK
    entry["domains"] = parse_domains(A)

    #entry["notes"] = parse_notes(A)

    #entry["usages"] = parse_usage(A)

    #entry["forums"] = parse_forums(A)

    # Parse P element for words
    P = A.find(".//h:P", namespaces={"h": "http://www.eki.ee/dict/har"})
    if P is not None:
        entry["words"] = parse_words(P, A)

    # Parse S element for definitions
    S = A.find(".//h:S", namespaces={"h": "http://www.eki.ee/dict/har"})
    if S is not None:
        entry["definitions"] = parse_definitions(S)

    # OK
    entry["conceptIds"] = parse_concept_ids(A)

    return entry

def parse_xml(input_filename, output_filename):
    tree = ET.parse(input_filename)
    root = tree.getroot()

    entries = []

    for A in root.findall(".//h:A", namespaces={"h": "http://www.eki.ee/dict/har"}):
        entry = parse_entry(A)
        entries.append(entry)

    json_output = json.dumps(entries, indent=4, ensure_ascii=False)

    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(json_output)