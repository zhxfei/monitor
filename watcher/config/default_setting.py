import os

DEFAULT_AUTH_NAME = os.getenv('WATCH_USER', 'zhxfei')
DEFAULT_AUTH_PASSWORD = os.getenv('WATCH_PASSWORD', 'zhxfei')
DEFAULT_AUTH = (DEFAULT_AUTH_NAME, DEFAULT_AUTH_PASSWORD)

API_URL = "http://localhost:11111/monitor/v1"

DEFAULT_PULLER_PASSWORD = os.getenv("REDIS_PASS", None)

DEFAULT_PULLER_CONF = {
    "queue_suffix": "monitor_queue_watcher",
    "backend_type": "watcher",
    "connection_params": {
        "host": "localhost",
        "port": 6379,
        "db": 1,
        "password": DEFAULT_PULLER_PASSWORD
    }
}
