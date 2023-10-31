import logging
import os
import datetime
import sys

def get_logger():
    logger = logging.getLogger(__name__)
    logger.propagate = False
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        if not os.path.exists('logs'):
            os.mkdir('logs')

        now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_name = f'logs/import_log_{now}.log'
        file_handler = logging.FileHandler(file_name, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
