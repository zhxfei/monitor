import os

import redis


class RedisConnPool:
    def __init__(self, host=None, port=None, db=None, password=None):
        self.conn = redis.StrictRedis(host=host, port=port, db=db, password=password)

    def status_check(self):
        return self.conn.ping()
