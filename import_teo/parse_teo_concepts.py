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
        all_elements = dg.findall(".//x:all", namespaces={"x": "http://www.eki.ee/dict/teo"})

        for evt in A.findall(".//x:evt", namespaces={"x": "http://www.eki.ee/dict/teo"}):
            if evt.text:
                notes_list.append({
                    "value": "Vt ka: " + evt.text,
                    "lang": "est",
                    "publicity": True if is_concept_public(A) else False
                })

        sourceLinks = []
        for all_element in all_elements:
            if all_element is not None:
                sourceLinks.append(
                    {
                        "sourceId": get_source_id(all_element.text),
                        "value": all_element.text,
                        "name": ""
                    }
                )

        if lisa is not None and lisa.text:
            notes_list.append({
                "value": lisa.text,
                "lang": "est",
                "publicity": True if is_concept_public(A) else False,
                "sourceLinks": sourceLinks
            })



        for terg in A.findall(".//x:terg", namespaces={"x": "http://www.eki.ee/dict/teo"}):
            for etgg in terg.findall(".//x:etgg", namespaces={"x": "http://www.eki.ee/dict/teo"}):
                values = []
                for child in etgg:
                    if child.text:
                        values.append(child.text)
                if values:
                    concatenated_values = '; '.join(values)

                    ter = terg.find(".//x:ter", namespaces={"x": "http://www.eki.ee/dict/teo"})
                    if ter is not None:
                        concatenated_values = f"{ter.text} - {concatenated_values}"

                    notes_list.append({
                        "value": concatenated_values,
                        "lang": "est",
                        "publicity": True if is_concept_public(A) else False,
                        "sourceLinks": []
                    })

    confession = A.findall(".//x:konf", namespaces={"x": "http://www.eki.ee/dict/teo"})
    for c in confession:
        notes_list.append({
            "value": c.text,
            "lang": "est",
            "publicity": True if is_concept_public(A) else False,
            "sourceLinks": []
        })

    author = A.find(".//x:T", namespaces={"x": "http://www.eki.ee/dict/teo"})
    if author is not None:
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


def parse_usage(A):
    usages = []
    for ng in A.findall(".//x:ng", namespaces={"x": "http://www.eki.ee/dict/teo"}):
        n_element = ng.find(".//x:n", namespaces={"x": "http://www.eki.ee/dict/teo"})
        nall_element = ng.find(".//x:nall", namespaces={"x": "http://www.eki.ee/dict/teo"})

        sourceLinks = []
        if nall_element is not None:
            sourceLinks.append(
                {
                    "sourceId": get_source_id(nall_element.text),
                    "value": nall_element.text,
                    "name": ""
                }
            )

        if n_element is not None:
            usages.append({
                "value": n_element.text,
                "lang": "est",
                "publicity": True if is_concept_public(A) else False,
                "sourceLinks": sourceLinks
            })

    return usages


def parse_words(P, A):
    words = []

    for terg in P.findall(".//x:terg", namespaces={"x": "http://www.eki.ee/dict/teo"}):
        ter = terg.find(".//x:ter", namespaces={"x": "http://www.eki.ee/dict/teo"})
        tall = terg.find(".//x:tall", namespaces={"x": "http://www.eki.ee/dict/teo"})
        etym = terg.find(".//x:etym", namespaces={"x": "http://www.eki.ee/dict/teo"})

        liik_value = ter.attrib.get('{http://www.eki.ee/dict/teo}liik', None)

        if etym:
            lang = etym.text
        elif liik_value == 'z':
            lang = 'lad'
        else:
            lang = 'est'

        lexemeValueStateCode = ter.attrib.get('{http://www.eki.ee/dict/teo}tyyp', '')
        if lexemeValueStateCode == 'ee':
            lexemeValueStateCode = 'eelistermin'
        else:
            lexemeValueStateCode = None

        sourceLinks = []
        if tall is not None:
            sourceLinks.append(
                {
                    "sourceId": get_source_id(tall.text),
                    "value": tall.text,
                    "name": None
                })

        words.append({
            "value": ter.text,
            "lang": lang,
            "lexemeValueStateCode": [lexemeValueStateCode] if lexemeValueStateCode else None,
            "lexemePublicity": True if is_concept_public(A) else False,
            "sourceLinks": sourceLinks
        })

        # Handle the x:lyh element
        for lyh in terg.findall(".//x:lyh", namespaces={"x": "http://www.eki.ee/dict/teo"}):
            words.append({
                "value": lyh.text,
                "lang": None,
                "wordTypeCodes": ["lyhend"],
                "lexemePublicity": True if is_concept_public(A) else False,
                "sourceLinks": []
            })

    for xp in A.findall(".//x:xp", namespaces={"x": "http://www.eki.ee/dict/teo"}):
        lang = xp.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', '')
        for x in xp.findall(".//x:x", namespaces={"x": "http://www.eki.ee/dict/teo"}):
            words.append({
                "value": x.text,
                "lang": lang,
                "lexemePublicity": True if is_concept_public(A) else False,
                "wordTypeCodes": [],
                "sourceLinks": []
            })

        # Handle the x:xlyh element
        for xlyh in xp.findall(".//x:xlyh", namespaces={"x": "http://www.eki.ee/dict/teo"}):
            words.append({
                "value": xlyh.text,
                "lang": lang,
                "lexemePublicity": True if is_concept_public(A) else False,
                "wordTypeCodes": ["lühend"],
                "sourceLinks": []
            })

    for xp in A.findall(".//x:xp", namespaces={"x": "http://www.eki.ee/dict/teo"}):
        lang = xp.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', '')
        for xg in xp.findall(".//x:xg", namespaces={"x": "http://www.eki.ee/dict/teo"}):
            x = xg.find(".//x:x", namespaces={"x": "http://www.eki.ee/dict/teo"})
            if x is not None:
                lexemeNotes = []

                xgrg = xg.find(".//x:xgrg", namespaces={"x": "http://www.eki.ee/dict/teo"})
                if xgrg is not None:
                    for child in xgrg:
                        if child.text:
                            note = {
                                "value": child.text,
                                "lang": lang,
                                "publicity": True if is_concept_public(A) else False,
                            }
                            lexemeNotes.append(note)

                words.append({
                    "value": x.text,
                    "lang": lang,
                    "wordTypeCodes": [],
                    "lexemePublicity": True if is_concept_public(A) else False,
                    "sourceLinks": [],
                    "lexemeNotes": lexemeNotes if lexemeNotes else None
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


def parse_entry(A, dataset_code):
    if '{http://www.eki.ee/dict/teo}as' in A.attrib and A.attrib['{http://www.eki.ee/dict/teo}as'] == 'elx':
        print("test")
        return None

    entry = {}

    entry["datasetCode"] = dataset_code

    entry["domains"] = parse_domains(A)

    S = A.find(".//x:S", namespaces={"x": "http://www.eki.ee/dict/teo"})
    if S is not None:
        entry["definitions"] = parse_definitions(S)

    entry["notes"] = parse_notes(A)

    entry["usages"] = parse_usage(A)

    entry["forums"] = parse_forums(A)

    P = A.find(".//x:P", namespaces={"x": "http://www.eki.ee/dict/teo"})
    if P is not None:
        entry["words"] = parse_words(P, A)

    entry["conceptIds"] = parse_concept_ids(A)

    return entry

def parse_xml(input_filename, output_filename, dataset_code):
    tree = ET.parse(input_filename)
    root = tree.getroot()

    entries = []

    for A in root.findall(".//x:A", namespaces={"x": "http://www.eki.ee/dict/teo"}):
        entry = parse_entry(A, dataset_code)
        if entry:
            entries.append(entry)

    json_output = json.dumps(entries, indent=4, ensure_ascii=False)

    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(json_output)


def get_source_id(source_name):
    source_dict = {
        "Salumaa 2008": 22637,
        "EVÕSS": 16733,
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
        "EKSS": 0,
        "ПЭ": 22973,
        "ÕS 2018": 0,
        "EncChr": 22918,
        "Riistan 2011": 22969,
        "Blackwell": 22970,
        "Day": 22971,
        "BibleGateway": 22972,
        "BERTA": 19301
    }

    source_id = source_dict.get(source_name, None)

    if source_id is None:
        print(f"Source name not found: {source_name}")

    return source_id


def is_concept_public(A):
    TL = A.find(".//x:TL", namespaces={"x": "http://www.eki.ee/dict/teo"})
    if TL is not None and TL.text:
        return True
    else:
        return False