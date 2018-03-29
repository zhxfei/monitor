from transfer.exceptions.queue_exception import QueueFullException


class Queue:
    default_queue_len = 10000

    def __init__(self):
        self.queue_len = Queue.default_queue_len
        self.queue_suffix = 'easy_monitor'


class RedisQueue(Queue):
    def __init__(self,
                 max_queue_len=10000,
                 queue_suffix='easy_monitor',
                 backend_type=None,
                 conn=None):
        super(RedisQueue, self).__init__()

        self.max_queue_len = max_queue_len
        self.queue_name = queue_suffix + ':' + backend_type
        self.queue = conn

    def put(self, data):
        if self.get_len() < self.max_queue_len:
            res = self.queue.lpush(self.queue_name, data)
            return res

        raise QueueFullException

    def get(self, batch):
        '''
        get data from queue
        :param batch:
        :return:
        (True, data_lst) is mean the redis queue is empty, data_lst is the last data
        (False, data_lst) is mean the redis queue is not empty, data_lst is  data
        '''
        count = 0
        data_lst = list()

        if not self.queue.exists(self.queue_name):
            return True, None

        while count < batch:
            # redis pop data is a byte type
            data = self.queue.brpop(self.queue_name, timeout=1)
            if data:
                data_lst.append(data[1].decode('utf-8'))
                count += 1
            else:
                break

        return count < batch, data_lst

    def get_len(self):
        return self.queue.llen(self.queue_name)

    def check_status(self):
        return self.queue.ping()
