from ast import literal_eval

from .exceptions import QueueFullException


class BaseQueue:
    def __init__(self, max_queue_len=10000, queue_suffix='easy_monitor',
                 backend_type=None, connection=None):
        self.max_queue_len = max_queue_len
        self.queue_name = queue_suffix + ':' + backend_type
        self.queue = connection

    def put(self, request):
        """Push a data"""
        raise NotImplementedError

    def get(self, batch, timeout=0):
        """Pop a data"""
        raise NotImplementedError

    def get_len(self):
        raise NotImplementedError

    def __len__(self):
        return self.get_len()


class RedisQueue(BaseQueue):
    """ this is a fifo Queue by redis """

    def put(self, data):
        if self.get_len() < self.max_queue_len:
            res = self.queue.lpush(self.queue_name, data)
            return res

        raise QueueFullException

    def get(self, batch, timeout=1):
        '''
        get data from queue
        :param batch:
        :param timeout:
        :return: tuple
            tuple(True, data_lst) is mean the redis queue is empty
                        data_lst is the last data
            tuple(False, data_lst) is mean the redis queue is not empty,
                        data_lst is  data and type(data) is list with dict
        '''
        count = 0
        data_lst = list()

        if not self.queue.exists(self.queue_name):
            return True, None

        while count < batch:
            data = self.queue.brpop(self.queue_name, timeout=timeout)

            if isinstance(data, tuple):
                # redis pop data is a byte type
                # if redis list length > 0 , rpop data is a tuple (pop_queue_name, pop_res_data)
                data_lst.append(literal_eval(data[1].decode('utf-8')))
                count += 1
            else:
                # if redis list length = 0 or not exists, rpop data is None
                break

        return count < batch, data_lst

    def get_len(self):
        return self.queue.llen(self.queue_name)
