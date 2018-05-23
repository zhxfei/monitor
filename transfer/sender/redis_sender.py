import logging

import gevent
from redis.exceptions import RedisError

from common.queue.exceptions import QueueFullException
from common.queue.conn_queue import RedisQueue


class RedisSender(RedisQueue):
    """
        Transfer Sender Module:
         send data from cache queue
    """

    def __init__(self, retry_times=None, wait_time=None, sleep_time=None,
                 queue_suffix=None, queue=None, backend_type=None, max_queue_len=None):
        # init redis queue
        super(RedisSender, self).__init__(
            max_queue_len=max_queue_len,
            backend_type=backend_type,
            connection_params=queue,
            queue_suffix=queue_suffix
        )
        # init transfer logic
        self.retry_times = retry_times
        self.wait_time = wait_time
        self.sleep_time = sleep_time

    def data_send(self, data):
        """ send data """
        try:
            self.put(data)
        except RedisError as error_:
            logging.error("redis error: %s", str(error_))
        except QueueFullException as error_:
            logging.error(str(error_))
        else:
            return True

    def send_to_backend(self, cache_queue):
        logging.info("%s ", self)
        while True:
            while not cache_queue.empty():
                data = cache_queue.get_nowait()
                res = self.data_send(data)
                if not res:
                    # resend thread may be blocked
                    gevent.spawn(self.retry_send_data, data)

            logging.debug("%s will sleep for %d" % (self, self.wait_time))
            gevent.sleep(self.wait_time)

    def retry_send_data(self, data):
        logging.debug('%s will be resend %d times' % (str(data), self.retry_times))
        count = 0
        while count < self.retry_times:
            try:
                gevent.sleep(self.wait_time)
                res = self.data_send(data)
                if res:
                    logging.info("%s resend succeed" % str(data))
                    return res
            except QueueFullException as e:
                logging.debug("%s , %s send retry %d" % (e, str(data), count))
                count += 1
        logging.info("%s resend failed" % str(data))
        return False

    def __str__(self):
        sender_info = "Sender %d send to Queue %s : %s" % (id(self), self.queue_name,
                                                           str(self.connection_params))
        return sender_info

    @classmethod
    def from_config(cls, config):
        return cls(**config)
