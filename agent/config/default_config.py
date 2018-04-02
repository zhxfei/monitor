DEFAULT_LOG_LEVEL = "INFO"

COLLECTOR_DEFAULT_CONF = {
    'hostname': '',
    'ip': '',
    'interval': 60,
    'ignore': []
}

TRANSFER_DEFAULT_CONF = {
    'host': 'localhost',
    'port': '4444',
    'timeout': 30,
    'heartbeat': 5
}

DEFAULT_COLLECT_INTERVAL = COLLECTOR_DEFAULT_CONF['interval']
DEFAULT_COLLECT_IGNORE = COLLECTOR_DEFAULT_CONF['ignore']

DEFAULT_QUEUE_MAXSIZE = 100000
DEFAULT_CONSUMER_NUM = 5

DEFAULT_SENDER_SLEEP_TIME = 0.5
