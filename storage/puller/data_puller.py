from common.queue.conn_queue import RedisQueue
from common.connections.conn_pool import RedisConnPool


class DataPuller:
    """
    max_queue_len=None, queue_suffix=None,
                 backend_type=None, connection_params=None):
    """
    def __init__(self, host=None, port=None, db=None, password=None,
                 queue_name=None, backend_type=None,
                 batch=None):
        self._queue_name = queue_name
        self._max_batch = batch

        self.queue = RedisQueue(
            queue_suffix=queue_name,
            backend_type=backend_type,
            connection=self._redis_conn.get_conn()
        )

    def status_check(self):
        return self._redis_conn.status_check()

    def pull_data(self):
        return self.queue.get(batch=self._max_batch, timeout=1)
