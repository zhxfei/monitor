# from gevent import monkey
#
# monkey.patch_all()
from pymongo import MongoClient


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
        self._document = self._db[document_name]

    def data_insert(self, data):
        try:
            res = self._document.insert_many(data)
            if len(res.inserted_ids) > 0:
                return True
            return False

        except Exception as e:
            print(e)
            return False

    def document_count(self):
        # for test connection
        return self._document.count()