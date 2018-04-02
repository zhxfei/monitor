import logging

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
    "concurrency_num": 1
}

DEFAULT_SENDER_CONF = {
    "retry_times": 2,
    "wait_time": 5,
    "sleep_time": 1,
    "queue_suffix": "monitor_queue",
    "queue": {
        "host": "localhost",
        "port": 6379,
        "db": 0
    }
}
