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
            tuple(True, data_lst) is mean the redis queue is empty, data_lst is the last data
            tuple(False, data_lst) is mean the redis queue is not empty, data_lst is  data
        '''
        count = 0
        data_lst = list()

        if not self.queue.exists(self.queue_name):
            return True, None

        while count < batch:
            # redis pop data is a byte type, and block rpop result is a tuple (pop_res_status, pop_res_data)
            data = self.queue.brpop(self.queue_name, timeout=timeout)

            if isinstance(data, tuple):
                data_lst.append(data[1].decode('utf-8'))
                count += 1
            else:
                break

        return count < batch, data_lst

    def get_len(self):
        return self.queue.llen(self.queue_name)
