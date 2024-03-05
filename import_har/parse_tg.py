import data_classes
import sources_helpers
import xml_helpers


# Mõiste tähendusgrupp: tg : def - Definitsiooniks jmt
def tg_def_definition(tg_element, sources_with_ids, conceptids, guid_word_dict, ns):
    def_value = None
    definition = None
    notes = []
    sourcelinks = []
    forums = []

    sources = []

    for dg_element in tg_element.findall('./h:dg', ns):
        for def_element in dg_element.findall('./h:def', ns):
            def_value = def_element.text
        for all_element in dg_element.findall('./h:all', ns):
            source_value = all_element.text
            s_id, s_name = sources_helpers.get_source_id_and_name_by_source_text(sources_with_ids, source_value)
            sourcelink = data_classes.Sourcelink(
                sourceId=s_id,
                value=s_name,
                name='')
            sourcelinks.append(sourcelink)
        for dn_element in dg_element.findall('./h:dn', ns):
            if def_value:
                def_value = def_value + ', nt ' + dn_element.text
            else:
                notes.append(data_classes.Note(
                    value=dn_element.text,
                    lang='est',
                    publicity=True,
                    sourceLinks=[]
                ))

    for co_element in tg_element.findall('./h:co', ns):
        notes.append(data_classes.Note(
            value=co_element.text,
            lang='est',
            publicity=True,
            sourceLinks=[]
        ))

    meaning_relations = []


    # Tesaurus
    # Tähenduse seosed (ant > antonüüm)
    for tes_element in tg_element.findall('./h:tes', ns):
        for child in tes_element:
            tag_name = child.tag.split('}')[-1]

            if tag_name == 'ant':
                if xml_helpers.find_guid_by_term(child.text, guid_word_dict):
                    meaning_relations.append(str(conceptids[0]) + '; antonüüm; ' + xml_helpers.find_guid_by_term(child.text, guid_word_dict))
                elif child.text:
                    print('Vigane antonüüm: ' + child.text)
                else:
                    print('Puudub antonüüm: ' + str(conceptids[0]))
            else:
                print('Muud tüüpi: ' + str(conceptids[0]))

    # Tähenduse seose viited (vrd, vt ka > seotud)
    for evt_element in tg_element.findall('./h:evt', ns):
        evt_value = evt_element.text if evt_element.text is not None else ""
        evt_attrib_value = evt_element.attrib.get(f'{{{ns["h"]}}}evtl', '')

        if evt_attrib_value == "vrd":
            if evt_value:
                if xml_helpers.find_guid_by_term(evt_value, guid_word_dict):
                    relation = str(conceptids[0]) + '; seotud; ' + xml_helpers.find_guid_by_term(evt_value, guid_word_dict)
                    meaning_relations.append(relation)
                else:
                    print('Vigane viide: ' + evt_value)
        elif evt_attrib_value == "vt ka":
            if evt_value:
                if xml_helpers.find_guid_by_term(evt_value, guid_word_dict):
                    relation = str(conceptids[0]) + '; seotud; ' + xml_helpers.find_guid_by_term(evt_value, guid_word_dict)
                    meaning_relations.append(relation)
                else:
                    print('Vigane viide: ' + evt_value)
        else:
            continue

    if def_value:
        definition = data_classes.Definition(
            value=def_value,
            lang='est',
            definitionTypeCode='definitsioon',
            sourceLinks=sourcelinks)

    # Sisemärkus
    forum = None
    for mrk_element in tg_element.findall('./h:mrk', ns):
        mrk_maut_value = mrk_element.attrib.get(f'{{{ns["h"]}}}maut', '')
        mrk_maeg_value = mrk_element.attrib.get(f'{{{ns["h"]}}}maeg', '')
        forum_value = mrk_element.text
        if forum_value.startswith('['):
            search_value = forum_value.strip().strip('[').strip(']')
            s_id, s_name = sources_helpers.get_source_id_and_name_by_source_text(sources_with_ids, search_value)
            definition.sourceLinks.append(data_classes.Sourcelink(
                sourceId=s_id,
                value=s_name,
                name=''
            ))
            continue
        elif forum_value.startswith('DEF: '):
            search_value = forum_value.replace('DEF: ', '').strip().strip('[').strip(']')
            s_id, s_name = sources_helpers.get_source_id_and_name_by_source_text(sources_with_ids, search_value)
            definition.sourceLinks.append(data_classes.Sourcelink(
                sourceId=s_id,
                value=s_name,
                name=''
            ))
            continue
        forum = data_classes.Forum(
            value=forum_value + ' (' + mrk_maut_value + ', ' + mrk_maeg_value + ')'
        )

    if forum is not None:
        forums.append(forum)

    return definition, notes, forums, sources, meaning_relations



