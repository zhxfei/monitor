import logging
import os
import signal
import sys

import gevent
import redis
from gevent.queue import Queue

from common.connections.conn_pool import RedisConnPool
from common.queue.conn_queue import RedisQueue
from transfer.config.config_parser import TransferConfigParser
from transfer.receiver.recv_http_server import HTTPServer
from transfer.receiver.recv_rpc_server import RPCServer
from transfer.sender.redis_sender import send_to_backend


class Router:
    def __init__(self):
        self.config = None
        self.basic_info = dict()
        self.backend_lst = list()
        self.queue_map = dict()
        self.conn_map = dict()
        self.cache_queue_map = dict()

    def config_init(self, config_path):
        """config init"""
        self.config = TransferConfigParser(config_path)
        self._log_init()
        self._service_init()

    def _service_init(self):
        """ init config by routers function"""
        try:
            self._router_init()
            self._receiver_conf_init()
            self._sender_conf_init()
        except KeyError as e:
            logging.error("!!! Service config load error")
            logging.error(e)
            sys.exit(1)

    def _router_init(self):
        self._backend_nodes_init()
        self._conn_pool_init()
        self._queue_init()
        self._concurrency_init()

    def _log_init(self):
        """ log init """
        logging.basicConfig(
            filename=self.config.var_dict.get('logfile') or None,
            level=logging.DEBUG if self.config.var_dict.get('debug') else logging.INFO,
            format='%(levelname)s:%(asctime)s:%(message)s'
        )

    def _backend_nodes_init(self):
        if self.config.var_dict.get('data_store'):
            self.backend_lst.append('store')
        if self.config.var_dict.get('data_judge'):
            self.backend_lst.append('judge')
        logging.info("backend list config: %s" % ",".join(self.backend_lst))

    def _conn_pool_init(self):
        """ connection pool init """
        try:
            for queue_type in self.backend_lst:
                # if $REDIS_PASS not exists, means redis access don't require password
                redis_pass = os.getenv('REDIS_PASS')
                redis_info = self.config.var_dict['queue'].get(queue_type)
                if redis_info:
                    conn = RedisConnPool(
                        host=redis_info['host'],
                        port=redis_info['port'],
                        db=redis_info['db'],
                        password=redis_pass
                    ).get_conn()

                    self.conn_map[queue_type] = conn
                else:
                    logging.error("redis connection init failed")
        except redis.exceptions.ConnectionError as e:
            logging.error(e)
            sys.exit(2)
        except ValueError as e:
            logging.error(e)
            sys.exit(3)

    def _queue_init(self):
        """ cache queue and redis queue init """
        max_queue_len = self.config.var_dict['queue']['max_queue_len']
        queue_suffix = self.config.var_dict['queue']['queue_suffix']
        cache_queue_len = self.config.var_dict['cache_queue']['max_queue_len']

        if self.config.var_dict['queue']['type'] == 'redis':
            for queue_type in self.backend_lst:
                redis_queue = RedisQueue(
                    backend_type=queue_type,
                    max_queue_len=max_queue_len,
                    queue_suffix=queue_suffix,
                    connection=self.conn_map[queue_type]
                )

                self.queue_map[queue_type] = redis_queue
                cache_queue = Queue(maxsize=cache_queue_len)
                self.cache_queue_map[queue_type] = cache_queue

                logging.info("Queue %s init succeed" % queue_type)

    def _concurrency_init(self):
        """ greenlet numbers init , every backend will get concurrency number greenlets"""
        self.concurrency_num = self.config.var_dict.get('concurrency_num') or 1
        logging.info('concurrency config %d' % self.concurrency_num)

    def _sender_conf_init(self):
        """ sender init """
        self.sender_sleep_times = self.config.var_dict['sleep_time']

        # when redis queue is full, sender will retry some times
        self.sender_retry_times = self.config.var_dict['retry_times']

        # when redis queue is full, sender will retry and wait some time
        self.sender_wait_time = self.config.var_dict['wait_time']

    def _receiver_conf_init(self):
        """ receiver config init , include a web api and rpc server, for data upload from agent"""
        self._rpc_srv_conf_init()
        self._http_conf_init()

    def _rpc_srv_conf_init(self):
        """init rpc server basic config, agent will use it """
        self._rpc_server_listen = self.config.var_dict['rpc']['listen']
        self._rpc_server = RPCServer(
            listen=self._rpc_server_listen,
            cache_queue_map=self.cache_queue_map
        )

    def _http_conf_init(self):
        """init http server basic config, common API for data upload"""
        self._http_server_host = self.config.var_dict['http']['host']
        self._http_server_port = self.config.var_dict['http']['port']
        self._http_server = HttpServer(
            http_host=self._http_server_host,
            http_port=self._http_server_port,
            cache_queue_map=self.cache_queue_map
        )

    def send_to_queue(self, q_name, cache_q):
        redis_q = self.queue_map[q_name]
        while True:
            logging.debug('Queue name: %s, len: %d' % (q_name, len(cache_q)))

            send_to_backend(redis_q, cache_q, self.sender_wait_time, self.sender_retry_times)

            logging.debug('Queue is empty, greenlet will be sleep %d s' % self.sender_sleep_times)
            gevent.sleep(self.sender_sleep_times)

    def transfer_loop(self):
        """ all function modules start"""
        gevent.signal(signal.SIGQUIT, gevent.kill)

        job_lst = list()

        job_lst.append(gevent.spawn(self._rpc_server.server_forever))
        job_lst.append(gevent.spawn(self._http_server.serve_forever))

        for _ in range(0, self.concurrency_num):
            for q_name, cache_q in self.cache_queue_map.items():
                job_lst.append(gevent.spawn(self.send_to_queue, q_name, cache_q))

        logging.info("transfer loop started")

        gevent.joinall(job_lst)