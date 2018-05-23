"""
 the module define puller component, get data from redis queue
"""
import logging

from common.queue.conn_queue import RedisQueue
from common.queue.exceptions import QueueFullException
from redis.exceptions import RedisError


class DataPuller(RedisQueue):
    """
        push and pull data from redis list
    """

    def push_data(self, msg, queue_name):

        try:
            self.put(msg, queue_name=queue_name)
        except QueueFullException:
            logging.error("queue %s full" % queue_name)
        except RedisError as error_:
            logging.error(error_)
        else:
            return True

    def pull_data(self, batch):
        res = None
        try:
            res = self.get(batch=batch, timeout=1)
        except RedisError as error_:
            logging.error(error_)
        finally:
            return res

    @classmethod
    def from_config(cls, config):
        return cls(**config)
