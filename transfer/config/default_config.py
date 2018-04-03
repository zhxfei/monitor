"""
 This module set the default config
"""

import logging
import os

DEFAULT_LOG_LEVEL = logging.INFO

DEFAULT_HTTP_CONF = {
    "host": "0.0.0.0",
    "port": 4445
}

DEFAULT_RPC_SERVER_CONF = {
    "host": "0.0.0.0",
    "port": 4445
}

DEFAULT_ROUTER_CONF = {
    "max_queue_len": 100000,
    "concurrency_num": 1,
    "backend_nodes": ['store']
}

DEFAULT_SENDER_CONF = {
    "max_queue_len": 100000,
    "retry_times": 2,
    "wait_time": 5,
    "sleep_time": 1,
    "queue_suffix": "monitor_queue",
    "queue": {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": os.getenv('REDIS_PASS', None)
    }
}

SENDER_TYPE_REDIS = 'redis'
