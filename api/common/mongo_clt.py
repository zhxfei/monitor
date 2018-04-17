# from gevent import monkey
#
# monkey.patch_all()
from common.connections.mongo_conn import MONGOClient
from api.common.mongo_setting import DEFAULT_DB_CONF


def create_conn():
    try:
        clt = MONGOClient.from_config(DEFAULT_DB_CONF)
    except ValueError:
        return None
    else:
        return clt.document
