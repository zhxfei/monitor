"""
 the module define mongodb client
"""
#
import logging

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class MONGOClient:
    # cache_map = dict()

    def __init__(self, host=None, port=None,
                 name=None, user=None, password=None, document_name=None):
        self.db_url = "mongodb://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        self.connection = MongoClient(self.db_url.format(db_user=user,
                                                         db_pass=password,
                                                         db_host=host,
                                                         db_port=port,
                                                         db_name=name))
        self._db = self.connection[name]
        self.document = self._db[document_name]
        if not self.status_check():
            raise ValueError('Mongo client init failed, connect error: %s:%d' % (host, port))

    def document_new(self, document_name):
        return self._db[document_name]

    def data_insert(self, data):
        """ insert data to the document"""
        try:
            res = self.document.insert_many(data)
            return len(res.inserted_ids) > 0

        except TypeError as error_info:
            logging.error(error_info)
            return False

    def status_check(self):
        """check mongodb connect succeed"""
        try:
            # The is_master command is cheap and does not require auth.
            self.connection.admin.command('ismaster')
        except ConnectionFailure:
            return False
        else:
            return True

    def document_count(self):
        """ test the document writeable"""
        return self.document.count()

    @classmethod
    def from_config(cls, config):
        """ get instance from config"""
        return cls(**config)
