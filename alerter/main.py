# coding: utf-8
import time
import logging
from ast import literal_eval
from datetime import datetime

import threading
from queue import Queue

from common.connections.redis_conn_pool import RedisConnPool
from alerter.sender import MailServer
from alerter.default_setting import (DEFAULT_REDIS_CONF,
                                     DEFAULT_QUEUE_NAME,
                                     JUDGE_MESSAGE,
                                     ALERTER_URL)
from watcher.net import UrlFetcher


class Alerter:
    def __init__(self):
        self.conn = RedisConnPool.from_config(DEFAULT_REDIS_CONF).get_conn()
        self.queue = Queue()
        # self.sender_pool = Pool(5)
        self.info_fetcher = UrlFetcher(ALERTER_URL)
        self.mail_server = MailServer()
        self.send_status_cache = dict()

    def pull_judge_event(self, queue_name=DEFAULT_QUEUE_NAME):
        while True:
            try:
                res = self.conn.rpop(queue_name)
                if res is not None:
                    self.queue.put(literal_eval(res.decode('utf-8')))
                else:
                    time.sleep(2)
            except Exception as e:
                logging.error(e)

    def alert_main(self):
        while True:
            data = self.queue.get()
            if data is not None:
                monitor_id, message = self._message_parse(data)

                self._alert_main(monitor_id, message, data)

    def _alert_main(self, monitor_id, message, raw_message):
        alert_item_data = self._get_item_lst(monitor_id)
        if isinstance(alert_item_data, list):
            email_lst = [(alert_item.get('convergence_time'), alert_item.get('email'))
                         for alert_item in alert_item_data if alert_item.get('type') == 'email']

            key = self.gen_key(raw_message)
            if key not in self.send_status_cache:
                logging.debug("message will send")
                res = self.send_message(email_lst, message)
                if res:
                    self.send_status_cache[key] = raw_message.get('time')
            else:
                convergence_time = int(alert_item_data[0].get('convergence_time'))
                old_time = self.send_status_cache[key]

                if raw_message.get('time') - old_time > convergence_time:
                    logging.debug("message will fresh and send")
                    res = self.send_message(email_lst, message)
                    if res:
                        self.send_status_cache[key] = raw_message.get('time')
                else:
                    logging.debug("convergence_time succeed")

    def _get_item_lst(self, monitor_id):
        response = self.info_fetcher.fetch()
        if response is not None and response.status_code == 200:
            alert_item_data = response.json()
            alert_item_data = [instance_data
                               for instance_data in alert_item_data
                               if instance_data['monitor_id'] == monitor_id]

            return alert_item_data

    @staticmethod
    def _message_parse(data):
        monitor_id = data.get('monitor_id')
        message = JUDGE_MESSAGE.format(tags=str(data.get('tags')),
                                       metrics=data.get('metrics'),
                                       time=datetime.fromtimestamp(data.get('time')),
                                       condition=data.get('condition'),
                                       value=data.get('value'))
        return monitor_id, message

    def send_message(self, email_lst, message):
        res = None
        for _, _email in email_lst:
            res = self.mail_server.mail_send(_email, message)
        return res

    @staticmethod
    def gen_key(params):
        metrics = params.get('metrics')
        tags = params.get('tags')
        monitor_id = params.get('monitor_id')
        key_ = metrics + str(tags) + monitor_id
        return hash(key_)


if __name__ == '__main__':
    import argparse

    description = '''Monitor alert design for alert message send'''

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-l', '--log',
                        metavar='LOG_FILE_PATH',
                        required=False,
                        default='./alert.log',
                        dest='log_path',
                        action='store',
                        help='define Monitor alert log file path')
    parser.add_argument('--level',
                        metavar='LOG_LEVEL',
                        required=False,
                        default=logging.DEBUG,
                        dest='log_level',
                        action='store',
                        help='''
                            define Monitor alert log level
                            example:
                            CRITICAL = 50
                            ERROR = 40
                            WARNING = 30
                            INFO = 20
                            DEBUG = 10
                            ''')

    args = parser.parse_args()
    logging.basicConfig(
        filename=args.log_path,
        level=args.log_level,
        format="[%(asctime)s] >>> %(levelname)s  %(name)s: %(message)s"
    )
    logging.info('Monitor Alerter init succeed...')

    alert = Alerter()

    job_lst = list()

    t1 = threading.Thread(target=alert.pull_judge_event)
    t1.start()
    job_lst.append(t1)

    t2 = threading.Thread(target=alert.alert_main)
    job_lst.append(t2)
    t2.start()

    for t in job_lst:
        t.join()
