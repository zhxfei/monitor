import time
import logging
from datetime import datetime

import gevent

from agent.collect.sys_status_collect import ps_utils_collect_funcs
from agent.config.default_config import DEFAULT_HOST_NAME, DEFAULT_IP


class Collector:
    """base collector"""

    def __init__(self, hostname=None, ip=None, interval=None, ignore=None):
        self.interval = interval
        self.ignore = ignore
        self.hostname = hostname or DEFAULT_HOST_NAME
        self.ip = ip or DEFAULT_IP

    def data_model_format(self, data, timestamps):
        """ data build format """
        data_lst = []
        for item_name, item_value in data.items():
            if item_name not in self.ignore:
                item_dict = {
                    "metric": item_name,
                    "timestamp": timestamps,
                    "step": self.interval,
                    "value": item_value,
                    "counterType": gen_counter_type(item_name),
                    "tags": {
                        "host_ip": self.ip,
                        "hostname": self.hostname
                    }
                }
                data_lst.append(item_dict)
        return data_lst

    def collector_loop(self, queue):
        """ data collect loop ,will called by agent main process"""
        raise NotImplementedError


class PsUtilsCollector(Collector):
    """collector by psutil package"""
    collect_funcs = ps_utils_collect_funcs

    def collector_loop(self, queue):
        """ get data forever , will called by agent main process"""
        self._collect_loop(queue)

    def _collect_loop(self, queue):
        """ collect data and put in queue """
        while True:
            t_start = time.time()
            now_timestamp = int(datetime.now().timestamp())

            for _, collect_func in self.collect_funcs.items():

                data = collect_func()
                format_data = self.data_model_format(data, now_timestamp)
                if format_data:
                    queue.put(format_data)
            cost_time = str(time.time() - t_start)

            logging.debug('Data Collect By %s Once Cost: %s' % ("PsUtilsCollector", cost_time))
            gevent.sleep(self.interval)

    @classmethod
    def from_config(cls, config):
        """ get instance from config
        :param config dict
            the dict with __init__ params
        """
        return cls(**config)


def gen_counter_type(metric_name):
    if metric_name.startswith('net.dev'):
        return 'COUNTER'
    else:
        return "GAUGE"
