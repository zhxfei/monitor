# from gevent import monkey
#
# monkey.patch_all()
from pymongo import MongoClient
from os import getenv


class DatabaseClient:
    def __init__(self,
                 db_host=None,
                 db_port=None,
                 db_name=None,
                 db_user=None,
                 db_pass=None,
                 document_name=None):
        self._db_document_name = document_name
        db_url = "mongodb://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        conn = MongoClient(db_url.format(db_user=db_user,
                                         db_pass=db_pass,
                                         db_host=db_host,
                                         db_port=db_port,
                                         db_name=db_name))
        self._db = conn[db_name]
        self.document = self._db[document_name]


def create_conn():
    clt = DatabaseClient(db_host='10.83.3.48',
                         db_port=30000,
                         db_name='easy_monitor',
                         db_user='easy_monitor',
                         db_pass=getenv('MONGO_PASS'),
                         document_name='monitor_60')
    return clt.document


