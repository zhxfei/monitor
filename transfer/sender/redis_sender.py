import logging

import gevent
from gevent.pool import Pool
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
        self.pool = Pool(1000)

        # self.pool.start()

    def data_send(self, data):
        """ send data """
        try:
            self.put(data)
        except RedisError as error_:
            logging.error("redis error: %s", str(error_))
        except QueueFullException as error_:
            logging.error("redis queue is full %s", str(error_))
        else:
            return True

    def send_to_backend(self, cache_queue):
        logging.info("%s ", self)
        while True:
            while not cache_queue.empty():
                data = cache_queue.get_nowait()

                # if self.pool.full():
                #     logging.error("At maximum pool size")
                #     self.pool.wait_available(3)
                # else:
                # self.pool.spawn(self._send_data, data)
                self._send_data(data)
                # gevent.spawn(self._send_data, data)
                    # res = self.data_send(data)
                # if res is None:
                #     # resend thread may be blocked
                #     try:
                #         gevent.spawn(self.retry_send_data, data)
                #     except OSError:
                #         logging.error("green let new too a lot")

            logging.debug("%s will sleep for %d" % (self, self.wait_time))
            gevent.sleep(self.wait_time)

    def _send_data(self, data):
        logging.debug('%s will be resend %d times' % (str(data), self.retry_times))
        count = 0
        while count < self.retry_times:
            res = self.data_send(data)
            if res:
                # logging.info("%s send succeed" % str(data))
                break
            else:
                gevent.sleep(self.wait_time)
                # logging.debug("%s send retry %d" % (str(data), count))
                count += 1

        if count < self.retry_times:
            logging.debug("%s send succeed" % str(data))
        else:
            logging.debug("%s send failed" % str(data))

    def __str__(self):
        sender_info = "Sender %d send to Queue %s : %s" % (id(self), self.queue_name,
                                                           str(self.connection_params))
        return sender_info

    @classmethod
    def from_config(cls, config):
        return cls(**config)
