# DEFINITIONS

import xml_helpers
import data_classes

ns = {
    'x': 'http://www.eki.ee/dict/has',
    'xml': 'http://www.w3.org/XML/1998/namespace'
}

def tg_def_definition(tg_element, sources_with_ids):
    def_value = None
    definition = None
    notes = []
    sourcelinks = []
    forums = []
    relations = []

    # Definitsioon
    for dg_element in tg_element.findall('./x:dg', ns):
        for def_element in dg_element.findall('./x:def', ns):
            def_value = def_element.text

        # Märkus
        for dn_element in dg_element.findall('./x:dn', ns):
            notes.append(data_classes.Note(
                value=dn_element.text.replace('&ema;', '<eki-foreign>').replace('&eml;', '</eki-foreign>'),
                lang='est',
                publicity=True,
                sourceLinks=[]
            ))

    # Märkus
    for co_element in tg_element.findall('./x:co', ns):
        note_value = co_element.text.replace('&ema;', '<eki-foreign>').replace('&eml;', '</eki-foreign>')
        notes.append(data_classes.Note(
            value=note_value,
            lang='est',
            publicity=True,
            sourceLinks=[]
        ))

    # Tesaurus
    for tes_element in tg_element.findall('./x:tes', ns):
        for child in tes_element:
            tag_name = child.tag.split('}')[-1]
            child_text = child.text if child.text is not None else ""
            if tag_name == 'ant':
                relations.append('antonüüm; ' + child_text)

    for evt_element in tg_element.findall('./x:evt', ns):
        evt_value = evt_element.text if evt_element.text is not None else ""
        relations.append('seotud mõiste; ' + evt_value)

    # Sisemärkus
    forum = None
    def_sourcelinks = []

    for mrk_element in tg_element.findall('./x:mrk', ns):
        mrk_maut_value = mrk_element.attrib.get(f'{{{ns["x"]}}}maut', '')
        mrk_maeg_value = mrk_element.attrib.get(f'{{{ns["x"]}}}maeg', '')
        forum_value = mrk_element.text

        if forum_value.startswith('['):
            s_id, s_value, s_inner = xml_helpers.get_source_id_and_name_by_source_text(sources_with_ids, forum_value.strip('[]'))
            def_sourcelink = data_classes.Sourcelink(
                sourceId=s_id,
                value=s_value,
                name=s_inner
            )
            def_sourcelinks.append(def_sourcelink)

        else:
            forum = data_classes.Forum(
                value=forum_value + ' (' + mrk_maut_value + ', ' + mrk_maeg_value + ')'
            )

    if forum is not None:
        forums.append(forum)

    if def_value:
        def_value = def_value.replace('&ema;', '<eki-foreign>').replace('&eml;', '</eki-foreign>')

        for all_element in dg_element.findall('./x:all', ns):
            source_value = all_element.text
            s_id, s_value, s_inner = xml_helpers.get_source_id_and_name_by_source_text(sources_with_ids, source_value)
            def_sourcelink = data_classes.Sourcelink(
                sourceId=s_id,
                value=s_value,
                name=s_inner)
            def_sourcelinks.append(def_sourcelink)

        definition = data_classes.Definition(
            value=def_value,
            lang='est',
            definitionTypeCode='definitsioon',
            sourceLinks=def_sourcelinks)

    return definition, notes, forums, relations