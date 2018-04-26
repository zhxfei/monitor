"""
    this module for mongo setting
"""
import os

DEFAULT_DB_CONF = {
    "host": "10.83.3.46",
    "port": 30000,
    "user": "easy_monitor",
    "password": os.getenv("MONGO_PASS", None),
    "name": "easy_monitor",
    "document_name": "monitor_dev_v2"
}
