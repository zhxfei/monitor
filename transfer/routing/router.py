import logging
import signal

import gevent
from gevent.queue import Queue

from transfer.config.config_parser import TransferConfigParser


class Router(object):
    def __init__(self):
        """
        route data from receiver to sender and help receiver/sender setup,
        router provide a cache_queue map, the map's key is backend type, like store or other, and value is a queue.

        receiver: a component for receive data from agent or any process who called API
                    by HTTP or RPC service, receiver will setup a http server and rpc server.
        router: receiver and sender helper, provide a cache queue map for backend,
                    receiver will push data in cache queue, and sender will consume the data.
        sender: send data to backend, pop data from cache queue and send to the backend.

        """
        self.config = None
        self.rpc_server = None
        self.http_server = None

        self.backend_nodes = list()
        self.sender_map = dict()
        self.cache_queue_map = dict()

    def config_init(self, config_path):
        """
        config init
        :param config_path: str
                init configuration
        """
        self.config = TransferConfigParser(config_path)
        self._log_init()

        self._router_init()
        self.sender_init()
        self.receiver_init()

    def _log_init(self):
        """ log init """
        logging.basicConfig(
            filename=self.config.var_dict.get('logfile') or None,
            level=logging.DEBUG if self.config.var_dict.get('debug') else logging.INFO,
            format='%(levelname)s:%(asctime)s:%(message)s'
        )
        logging.info('Transfer Log init succeed...')

    def _router_init(self):
        """ setup cache queue map """
        cache_queue_length = self.config.var_dict['router']['max_queue_len']
        self.backend_nodes = self.config.var_dict['router']['backend_nodes']

        # every backend server will get a cache queue
        for backend_node in self.backend_nodes:
            self.cache_queue_map[backend_node] = Queue(maxsize=cache_queue_length)

    def sender_init(self):
        """ setup sender"""
        # every backend server will init a sender to consume cache queue
        for backend_node in self.backend_nodes:
            self.sender_map[backend_node] = self.config.get_sender_from_config(backend_node)

    def receiver_init(self):
        """ receiver config init , include a web api and rpc server, for data upload from agent"""
        self.rpc_server = self.config.get_rpc_from_config(self.cache_queue_map)

        self.http_server = self.config.get_http_from_config(self.cache_queue_map)

    def transfer_loop(self):
        """
        transfer loop, receiver and sender serve forever
        """
        concurrency_num = self.config.var_dict['router']['concurrency_num']
        gevent.signal(signal.SIGQUIT, gevent.kill)

        job_lst = list()

        job_lst.append(gevent.spawn(self.rpc_server.serve_forever))
        job_lst.append(gevent.spawn(self.http_server.serve_forever))

        for backend_node, sender in self.sender_map.items():
            for _ in range(0, concurrency_num):
                job_lst.append(
                    gevent.spawn(sender.send_to_backend, self.cache_queue_map[backend_node])
                )

        logging.info("Transfer Loop started...")
        gevent.joinall(job_lst)
