import logging

from api.monitor.common.mongo_setting import DEFAULT_DB_CONF
from common.connections.mongo_conn import MONGOClient


def create_conn():
    try:
        clt = MONGOClient.from_config(DEFAULT_DB_CONF)
    except ValueError as error_info:
        logging.error(error_info)
        return None
    else:
        return clt
