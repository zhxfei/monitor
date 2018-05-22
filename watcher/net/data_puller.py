"""
 the module define puller component, get data from redis queue
"""
from common.queue.conn_queue import RedisQueue


class DataPuller(RedisQueue):
    """
        pull data from redis queue
    """

    def push_judge_msg(self, msg, queue_name):
        self.put(msg, queue_name=queue_name)

    def pull_data(self, batch):
        return self.get(batch=batch, timeout=1)

    @classmethod
    def from_config(cls, config):
        return cls(**config)
