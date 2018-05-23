import os

ALERTER_URL = "http://localhost:11111/monitor/v1/alert_items"

DEFAULT_PULLER_PASSWORD = os.getenv("REDIS_PASS", None)

DEFAULT_QUEUE_NAME = 'judge_to_alarm'

DEFAULT_REDIS_CONF = {
    "host": "localhost",
    "port": 6379,
    "db": 1,
    "password": DEFAULT_PULLER_PASSWORD,
}

JUDGE_MESSAGE = '''机器/机器组：{tags} 指标: {metrics} 在{time} 产生一个告警事件,监控的表达式为{condition},当前值为{value}'''

DEFAULT_EMAIL_USER = os.getenv("EMAIL_USER", "15852937839@163.com")
DEFAULT_EMAIL_PASS = os.getenv("EMAIL_PASS", None)
DEFAULT_EMAIL_SERVER = 'smtp.163.com'
