"""
    The module set default config for storage component
"""
import os
import logging

DEFAULT_PULLER_TYPE = 'redis'
DEFAULT_PULLER_PASSWORD = os.getenv("REDIS_PASS", None)

DEFAULT_DATABASE_TYPE = 'mongodb'

DEFAULT_PULLER_CONF = {
    "queue_suffix": "monitor_queue",
    "backend_type": "store",
    "connection_params": {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": DEFAULT_PULLER_PASSWORD
    }
}

DEFAULT_DB_CONF = {
    "host": "localhost",
    "port": 27017,
    "user": "ease_monitor",
    "password": os.getenv("MONGO_PASS", None),
    "name": "ease_monitor",
    "document_name": "monitor_data"
}

DEFAULT_BATCH = 98
DEFAULT_SLEEP = 0.5
DEFAULT_CONCURRENCY_NUM = 5
DEFAULT_LOG_LEVEL = logging.INFO
