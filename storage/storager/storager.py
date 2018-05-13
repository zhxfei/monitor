import signal
import logging

import gevent

from storage.config.config_parser import StorageConfigParser
from storage.config.default_config import (DEFAULT_LOG_LEVEL,
                                           DEFAULT_BATCH,
                                           DEFAULT_CONCURRENCY_NUM,
                                           DEFAULT_SLEEP)


class DataStorage:
    def __init__(self):
        self.config = None
        self.db_clt = None
        self.puller = None

        self.thread_sleep_time = None
        self.batch = None

    def config_init(self, config_path):
        self.config = StorageConfigParser(config_path)
        self._log_init()

        self._storage_init()
        self._db_conn_init()
        self._puller_init()

    def _log_init(self):
        """ log init """
        logging.basicConfig(
            filename=self.config.var_dict.get('logfile') or None,
            level=logging.DEBUG if self.config.var_dict.get('debug') else DEFAULT_LOG_LEVEL,
            format='%(levelname)s:%(asctime)s:%(message)s'
        )
        logging.info('logger init succeed')

    def _storage_init(self):
        """ storage init """
        self.thread_sleep_time = self.config.var_dict.get('thread_sleep') or DEFAULT_SLEEP
        self.batch = self.config.var_dict.get('batch') or DEFAULT_BATCH

        logging.info('node config init succeed')

    def _db_conn_init(self):
        """ setup the database connection"""
        self.db_clt = self.config.get_db_from_config()
        if self.db_clt is None:
            logging.error('DB connection init failed')
            raise SystemExit(4)
        else:
            logging.error('DB connection init failed')

    def _puller_init(self):
        """ setup the puller """
        try:
            self.puller = self.config.get_puller_from_config()
        except ValueError as error_info:
            logging.error('Puller init failed: %s' % error_info)
            raise SystemExit(5)
        except Exception as error_info:
            raise error_info
        else:
            logging.info('Puller init succeed')

    def _pull_and_storage(self, job_id):
        """
        pull data from queue and insert to database
        :param job_id: int
        """
        while True:
            while True:
                queue_is_empty, data = self.puller.pull_data(self.batch)
                if data:
                    status = self.db_clt.data_insert(data)
                    if status:
                        logging.debug("Pull data and insert Succeed")
                    else:
                        logging.error("Insert Error")

                if queue_is_empty:
                    break

            logging.debug("Queue is empty, job id: %d" % job_id)
            gevent.sleep(self.thread_sleep_time)

    def storage_forever(self):
        """ storage serve loop"""
        num = self.config.var_dict.get('concurrency_num') or DEFAULT_CONCURRENCY_NUM
        job_lst = list()

        gevent.signal(signal.SIGQUIT, gevent.kill)
        for job_id in range(0, num):
            job_lst.append(gevent.spawn(self._pull_and_storage, job_id))

        logging.info('Storage will serve forever')
        gevent.joinall(job_lst)
