"""
 the module define puller component, get data from transfer queue
"""

from common.queue.conn_queue import RedisQueue


class DataPuller(RedisQueue):
    """
        pull data from redis queue
    """

    def pull_data(self, batch):
        return self.get(batch=batch, timeout=1)

    @classmethod
    def from_config(cls, config):
        return cls(**config)
