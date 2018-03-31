import signal
import socket
import time
import logging
import sys
from datetime import datetime

import gevent

from agent.collector.data_collector_func import data_collect_funcs
from agent.config.config_parser import AgentConfigParser
from agent.rpc.send_rpc_client import RpcClient


class UnreachableException(Exception):
    pass


class MonitorAgent:
    default_collect_interval = 60

    # default_thread_timeout = 1

    def __init__(self):
        self.config = None
        self.collect_interval = None
        self.basic_info = {}
        self._rpc_server_host = None
        self._rpc_client = None
        self._collector_ignore_list = None

    def basic_init(self):
        self.basic_info['system.hostname'] = socket.gethostname()
        ip = socket.gethostbyname(self.basic_info['system.hostname'])
        self.basic_info['system.host_ip'] = ip if ip != 'localhost' else ""

    def config_init(self, config_path):
        self.basic_init()
        self.config = AgentConfigParser(config_path)
        self._log_init()
        self._endpoint_mart_init()
        self._rpc_srv_conf_init()
        self._collector_ignore_init()
        self._rpc_client_init()

    def _log_init(self):
        logging.basicConfig(filename=self.config.var_dict.get('logfile') or None,
                            level=logging.DEBUG if self.config.var_dict.get('debug') else logging.INFO,
                            format='%(levelname)s:%(asctime)s:%(message)s')

    def _endpoint_mart_init(self):
        if self.config.var_dict['hostname']:
            self.basic_info['system.hostname'] = self.config.var_dict['hostname']
        if self.config.var_dict['ip']:
            self.basic_info['system.host_ip'] = self.config.var_dict['ip']

    def _rpc_srv_conf_init(self):
        """init rpc server basic config"""
        transfer_addr = self.config.var_dict.get('transfer_addr')
        if not transfer_addr:
            logging.error('No useful routing rpc server')
            sys.exit(1)
        else:
            self._rpc_server_host = transfer_addr
            self.collect_interval = self.config.var_dict.get('collect_interval')
            logging.info('collect interval: %s s' % self.collect_interval)
            self._rpc_server_timeout = self.config.var_dict.get('transfer_timeout')
            self._rpc_server_hb = self.config.var_dict.get('transfer_headbeat')

    def _collector_ignore_init(self):
        """ set collector ignore list"""
        self._collector_ignore_list = self.config.var_dict.get('ignore') or None
        if self._collector_ignore_list:
            logging.info('Set ignore metric list: %s' % ",".join(self._collector_ignore_list))
        else:
            logging.info('Set no ignore metric list')

    def _rpc_client_init(self):
        self._rpc_client = RpcClient(self._rpc_server_host,
                                     timeout=self._rpc_server_timeout,
                                     heart_beat_itv=self._rpc_server_hb)

    def data_collect_loop(self):
        # prevent zombie processes
        gevent.signal(signal.SIGQUIT, gevent.kill)

        thread_lst = []

        for _, collect_func in data_collect_funcs.items():
            thread_lst.append(gevent.spawn(self.data_process_loop, collect_func))

        gevent.joinall(thread_lst)

    def data_process_loop(self, collect_func):
        while True:
            t_start = time.time()
            now_timestamp = int(datetime.now().timestamp())
            data = collect_func()
            processed_data = self.data_model_format(data, now_timestamp)
            if processed_data:
                self._data_push(processed_data)
            logging.debug('data process once cost: %s', str(time.time() - t_start))
            gevent.sleep(self.collect_interval)

    def _data_push(self, processed_data):
        logging.debug('data will send')
        response = self._rpc_client.send_mon_data(processed_data)
        if response and response.get('ok'):
            logging.debug('send monitor data succeed')
        else:
            logging.debug('send monitor data failed')

    def data_model_format(self, data, timestamps):
        if isinstance(data, dict):
            return self._data_model_build_no_tag(data, timestamps)
        else:
            return

    def _data_model_build_no_tag(self, data, timestamps):
        data_lst = []
        for item_name, item_value in data.items():
            item_dict = {
                "metric": item_name,
                "timestamp": timestamps,
                "step": self.collect_interval,
                "value": item_value,
                "counterType": 'GAUGE',
                "tags": {
                    "host_ip": self.basic_info['system.host_ip'],
                    "hostname": self.basic_info['system.hostname']
                }
            }
            data_lst.append(item_dict)
        return data_lst
