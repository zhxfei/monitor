import argparse
import logging
import sys

from transfer.routing.router import Router

if __name__ == '__main__':
    description = '''Monitor transfer design for data routing'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-c', '--config',
                        metavar='CONF_FILE_PATH',
                        required=False,
                        default='./transfer/transfer_config.json',
                        dest='config_path',
                        action='store',
                        help='define Monitor transfer configuration file path')
    args = parser.parse_args()

    try:
        data_transfer = Router()
        data_transfer.config_init(args.config_path)
        data_transfer.transfer_loop()

    except KeyboardInterrupt as e:
        logging.info("!!! Transfer exit")
        sys.exit(0)

    except Exception as e:
        logging.critical('!!! unknown problem')
        logging.critical(e)
        sys.exit(4)
