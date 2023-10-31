import requests
import json
from dotenv import load_dotenv
import os
import log_config
from collections import OrderedDict
import re

logger = log_config.get_logger()


load_dotenv()
api_key = os.environ.get("API_KEY")
parameters = {}
crud_role_dataset = os.environ.get("HAR")

header = {"ekilex-api-key": api_key}
parameters = {"crudRoleDataset": crud_role_dataset}


# Create a new source in Ekilex and return its ID
def create_source(source):
    logger.debug(f'Started creating source {source}')
    endpoint = "https://ekitest.tripledev.ee/ekilex/api/source/create"
    response = requests.post(endpoint, headers=header, params=parameters, json=source)

    if response.status_code >= 200 and response.status_code < 300:
        try:
            response_data = response.json()
            logger.info(f'Created source {source}. Response: {response_data}')
            return response_data['id']
        except json.JSONDecodeError:
            logger.warning(source)
            logger.warning(f"Failed to parse JSON from response when creating source Response text: {response.text}")

    else:
        logger.warning(source)
        logger.warning(f"Received non-200 response when creating source. "
                       f"Status code: {response.status_code}, Response text: {response.text}")
    return None

def assign_ids_to_all_sources(input_file, sources_with_ids_filename, ids_of_created_sources_filename):

    updated_sources = []
    ids_of_created_sources = []

    logger.info(f'Started assigning ID-s to all sources {input_file}')

    with open(input_file, 'r', encoding='utf-8') as f:
        count_existing_sources = 0
        count_created_sources = 0
        data = json.load(f)

        for source in data:
            print(source)
            source_id, was_created = create_source(source)
            if source_id:
                ordered_source = OrderedDict([('id', source_id)] + list(source.items()))
                updated_sources.append(ordered_source)
                if was_created:
                    ids_of_created_sources.append(source_id)
                    count_created_sources += 1
                else:
                    count_existing_sources += 1

    # Create a file with sources and their ID-s
    with open(sources_with_ids_filename, 'w', encoding='utf-8') as source_files_with_ids:
        json.dump(updated_sources, source_files_with_ids, ensure_ascii=False, indent=4)

    logger.info('Created file with sources and their ID-s')

    # Create a file with list of ID-s of created sources
    with open(ids_of_created_sources_filename, 'w', encoding='utf-8') as f:
        json.dump(ids_of_created_sources, f, ensure_ascii=False, indent=4)

    logger.info('Created file list of ID-s of created sources')
    logger.info('Number of existing sources: ' + str(count_existing_sources))
    logger.info('Number of created sources: ' + str(count_created_sources))
    return source_files_with_ids


def delete_created_sources(file):
    with open(file, 'r', encoding='utf-8') as file:
        source_ids = json.load(file)

    endpoint = "https://ekitest.tripledev.ee/ekilex/api/source/delete"

    for source_id in source_ids:
        params = {
            'sourceId': source_id,
            'crudRoleDataset': crud_role_dataset
        }

        response = requests.delete(endpoint, headers=header, params=params)

        if response.status_code >= 200 and response.status_code < 300:
            logger.info(f"Successfully deleted source with ID {source_id}.")
        else:
            logger.info(f"Failed to delete source with ID {source_id}. Status code: {response.status_code}, "
                        f"Response text: {response.text}")