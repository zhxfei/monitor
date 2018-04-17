from ast import literal_eval

from .exceptions import QueueFullException
from common.connections.redis_conn_pool import RedisConnPool


class BaseQueue:
    def __init__(
            self,
            max_queue_len=None,
            queue_suffix=None,
            backend_type=None,
            connection_params=None):
        """
        the base class for queue
        :param max_queue_len: int
                    queue max length.
        :param queue_suffix:  str
                    queue name suffix, for example: monitor:***
        :param backend_type:  str
                    backend type for set queue name, may be store or judge or other,
                    queue name is may be  queue_suffix:backend_type
        :param connection_params: dict
                    init connection for queue, the connections params depends on which queue you use,
                    may be redis or other
        """
        self.max_queue_len = max_queue_len
        self.queue_name = queue_suffix + ':' + backend_type
        self.connection_params = connection_params
        self.queue = None
        self.setup_queue()

    def setup_queue(self):
        """ init queue by connection_params"""
        raise NotImplementedError

    def put(self, data):
        """ Push data """
        raise NotImplementedError

    def get(self, batch, timeout=0):
        """ Pop data with batch """
        raise NotImplementedError

    def get_len(self):
        """ get queue length """
        raise NotImplementedError

    def __len__(self):
        return self.get_len()


class RedisQueue(BaseQueue):
    """ this is a fifo Queue by redis """

    def setup_queue(self):
        """set up queue config by redis connection"""
        conn_instance = RedisConnPool.from_config(self.connection_params)
        self.queue = conn_instance.get_conn()

    def put(self, data):
        """ push data in redis list, by left push"""
        if len(self) < self.max_queue_len:
            res = self.queue.lpush(self.queue_name, data)
            return res

        raise QueueFullException

    def get(self, batch, timeout=1):
        """
        pop data from queue in redis list, by right pop
        :param batch:   int
                data numbers queue pop once
        :param timeout: int
                when queue pop data, the operation will block and wait some time for data
        :return:    tuple
            True, data_lst is mean the redis queue is empty
                if data_lst is not None, and the data_lst is the final data in the queue
            False, data_lst is mean the redis queue is not empty,
                data_lst is  a list with pop data and data type is dict
        """
        count = 0
        data_lst = list()

        if not self.queue.exists(self.queue_name):
            return True, None

        while count < batch:
            data = self.queue.brpop(self.queue_name, timeout=timeout)

            if timeout is not 0 and isinstance(data, tuple):
                # redis pop data is a byte type
                # if redis list length > 0 , rpop data is a tuple (pop_queue_name, pop_res_data)
                data_lst.append(literal_eval(data[1].decode('utf-8')))
                count += 1
            else:
                # if redis list length = 0 or not exists, rpop data is None
                break

        return count < batch, data_lst

    def get_len(self):
        """ get queue length """
        return self.queue.llen(self.queue_name)

    @classmethod
    def from_config(cls, config):
        return cls(**config)
