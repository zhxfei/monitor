from common.connections.mongo_conn import MONGOClient
from api.common.mongo_setting import DEFAULT_DB_CONF


def create_conn():
    try:
        clt = MONGOClient.from_config(DEFAULT_DB_CONF)
    except ValueError:
        return None
    else:
        return clt.document


def create_user_conn():
    DEFAULT_DB_CONF.update({
        "document_name": "monitor_user"
    })
    try:
        clt = MONGOClient.from_config(DEFAULT_DB_CONF)
    except ValueError:
        return None
    else:
        return clt.document
