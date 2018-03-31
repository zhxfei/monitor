import signal
import os
import time
import logging
import sys

import gevent

from storage.config.config_parser import StorageConfigParser
from storage.puller.data_puller import DataPuller
from storage.db.mongo_clt import DatabaseClient


class DataStorage:
    def __init__(self):
        self.config = None
        self.basic_info = dict()
        self._node_name = None
        self.db_clt = None
        self.puller = None

    def basic_init(self):
        pass

    def config_init(self, config_path):
        self.basic_init()
        self.config = StorageConfigParser(config_path)
        self._log_init()
        try:
            self._node_init()
            self._db_conn_init()
            self._puller_init()
        except Exception as e:
            logging.error("!!! Service config load error")
            logging.error(e)
            sys.exit(2)

    def _log_init(self):
        """ log init """
        logging.basicConfig(filename=self.config.var_dict.get('logfile') or None,
                            level=logging.DEBUG if self.config.var_dict.get('debug') else logging.INFO,
                            format='%(levelname)s:%(asctime)s:%(message)s')

        logging.info('logger init succeed')

    def _node_init(self):
        self._node_name = self.config.var_dict['node_name']
        self._concurrency_num = self.config.var_dict.get('concurrency_num') or 10
        self._thread_sleep_time = self.config.var_dict.get('thread_sleep') or 2

        assert ":" not in self._node_name, ValueError("node name could't contains ':' !")
        logging.info('node config init succeed')

    def _db_conn_init(self):
        db_pass = os.getenv('MONGO_PASS', None)

        db_host = self.config.var_dict['database']['host']
        db_port = self.config.var_dict['database']['port']
        db_user = self.config.var_dict['database']['user']
        db_name = self.config.var_dict['database']['db_name']
        document_name = self.config.var_dict['database']['document_name']
        self.db_clt = DatabaseClient(db_host=db_host,
                                     db_port=db_port,
                                     db_name=db_name,
                                     db_user=db_user,
                                     db_pass=db_pass,
                                     document_name=document_name)
        _ = self.db_clt.document_count()
        logging.info('db connection init succeed')

    def _puller_init(self):
        if self.config.var_dict['queue']['type'] == 'redis':
            redis_pass = os.getenv('REDIS_PASS', None)

            redis_host = self.config.var_dict['queue']['addr']['host']
            redis_port = self.config.var_dict['queue']['addr']['port']
            redis_db = self.config.var_dict['queue']['addr']['db']
            queue_name = self.config.var_dict['queue']['queue_suffix'] + ":" + "store"
            self._batch = self.config.var_dict['queue']['batch']
            self.puller = DataPuller(host=redis_host,
                                     port=redis_port,
                                     db=redis_db,
                                     password=redis_pass,
                                     queue_name=queue_name,
                                     batch=self._batch)
        logging.info('redis connection init succeed')

    def _pull_and_storage(self, job_id):
        while True:
            while True:
                t1 = time.time()
                queue_is_empty, data = self.puller.pull_data()
                if data:
                    res = self.db_clt.data_insert(data)
                    if res:
                        logging.debug("insert succeed")
                        logging.debug("once insert {} data Cost:{}".format(self._batch, time.time() - t1))
                    else:
                        logging.error("insert error")

                if queue_is_empty:
                    break
            logging.debug("current greenlet id {} is free,queue is empty".format(job_id))
            gevent.sleep(self._thread_sleep_time)

    def storage_forever(self):
        gevent.signal(signal.SIGQUIT, gevent.kill)

        job_lst = list()
        for job_id in range(0, self._concurrency_num):
            job_lst.append(gevent.spawn(self._pull_and_storage, job_id))

        logging.info('storager will serve forever')
        gevent.joinall(job_lst)
