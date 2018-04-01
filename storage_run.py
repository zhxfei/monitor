import argparse
import logging
import sys

from storage.storager.storager import DataStorage

if __name__ == '__main__':
    # description = '''Monitor storage design for data storage, insert into Mongodb'''
    # parser = argparse.ArgumentParser(description=description)
    # parser.add_argument('-c',
    #                     '--config',
    #                     metavar='CONF_FILE_PATH',
    #                     required=False,
    #                     dest='config_path',
    #                     default='storage/storage_config.json',
    #                     action='store',
    #                     help='define Monitor transfer configuration file path')
    # args = parser.parse_args()

    try:
        data_store = DataStorage()
        data_store.config_init('./storage/storage_config.json')
        data_store.storage_forever()

    except KeyboardInterrupt as e:
        logging.info("!!! Storage exit")
        sys.exit(0)
    except Exception as e:
        logging.critical('!!! unknown problem')
        logging.critical(e)
        sys.exit(4)

