import redis


class RedisConnPool:
    def __init__(self, host=None, port=None, db=None, password=None):
        self._conn = redis.StrictRedis(host=host, port=port, db=db, password=password)

    def status_check(self):
        """
        check redis connection is healthy
        :return: boolean
        """
        return self._conn.ping()

    def get_conn(self):
        """make sure the connection is normal"""
        if not self.status_check():
            raise ValueError("Abnormal redis connection")

        return self._conn

