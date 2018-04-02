import logging
import signal

import gevent
from gevent.queue import LifoQueue

from agent.config.config_parser import AgentConfigParser
from agent.config.default_config import (DEFAULT_LOG_LEVEL,
                                         DEFAULT_QUEUE_MAXSIZE,
                                         DEFAULT_CONSUMER_NUM)


class MonitorAgent:
    """
        Monitor Agent: The main program logic
        :attr
            self.config    config parser
                read configuration from config file and get data sender and data collector
            self.collector
                for data collect class
            self.sender
                for data send class
            self.queue
                transfer data from collector to sender, it is a FIFO Queue
    """

    def __init__(self):
        self.config = None
        self.sender = None
        self.collector = None
        self.queue = LifoQueue(maxsize=DEFAULT_QUEUE_MAXSIZE)

    def config_init(self, config_path):
        """ config init from configuration file"""
        self.config = AgentConfigParser(config_path)
        self._log_init()
        self.sender_init()
        self.collector_init()

    def _log_init(self):
        """ init logging"""
        logging.basicConfig(
            filename=self.config.var_dict.get('logfile') or None,
            level=logging.DEBUG if self.config.var_dict.get('debug') else DEFAULT_LOG_LEVEL,
            format='%(levelname)s:%(asctime)s:%(message)s'
        )
        logging.info("Log init succeed")

    def sender_init(self):
        """ init sender module """
        self.sender = self.config.get_sender_from_config()
        logging.info("Sender init succeed")

    def collector_init(self):
        """ init data collector module """
        self.collector = self.config.get_collector_from_config()
        logging.info("Collector init succeed")

    def serve_forever(self):
        """ agent serve loop """

        gevent.signal(signal.SIGQUIT, gevent.kill)
        thread_lst = list()

        # producer
        thread_lst.append(gevent.spawn(self.collector.collector_loop, self.queue))

        # consumer
        for _ in range(0, DEFAULT_CONSUMER_NUM):
            thread_lst.append(gevent.spawn(self.sender.data_consume, self.queue))

        logging.info("Agent serve forever...")
        gevent.joinall(thread_lst)
