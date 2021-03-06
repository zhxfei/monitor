if __name__ == '__main__':
    from gevent import monkey

    monkey.patch_all()

    import argparse
    import logging
    import sys

    from storage.storager.storager import DataStorage

    description = '''Monitor storage design for data storage, insert into Mongodb'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-c', '--config',
                        metavar='CONF_FILE_PATH',
                        required=False,
                        default='./storage/storage_config.json',
                        dest='config_path',
                        action='store',
                        help='define Monitor transfer configuration file path')
    args = parser.parse_args()

    try:
        data_store = DataStorage()
        data_store.config_init(args.config_path)
        data_store.storage_forever()

    except KeyboardInterrupt as e:
        logging.info("!!! Storage exit")
        sys.exit(0)

    except Exception as e:
        logging.critical('!!! unknown problem')
        logging.critical(e)
        raise SystemExit(1)
