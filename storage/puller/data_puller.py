import redis
import logging
from ast import literal_eval


class DataPuller:
    def __init__(self,
                 host=None,
                 port=None,
                 db=None,
                 password=None,
                 queue_name=None,
                 batch=None):

        self._queue_name = queue_name
        self._max_batch = batch
        self.queue = redis.StrictRedis(host=host, port=port, db=db, password=password)

    def status_check(self):
        return self.queue.ping()

    def pull_data(self):
        '''
        get data from queue
        :param batch:
        :return:
        (True, data_lst) is mean the redis queue is empty, data_lst is the last data
        (False, data_lst) is mean the redis queue is not empty, data_lst is  data
        '''
        count = 0
        data_lst = list()

        if not self.queue.exists(self._queue_name):
            return True, None

        while count < self._max_batch:
            # redis pop data is a byte type
            data = self.queue.rpop(self._queue_name)
            if data:
                d = literal_eval(data.decode('utf-8'))
                data_lst.append(d)
                count += 1
            else:
                break

        return count < self._max_batch, data_lst
