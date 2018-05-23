# coding: utf-8
import time
import logging
from ast import literal_eval
from datetime import datetime

import threading
from queue import Queue
# from concurrent.futures import Pool

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

            if monitor_id not in self.send_status_cache:
                logging.debug("message will send")
                self.send_message(email_lst, message)
                self.send_status_cache[monitor_id] = raw_message.get('time')

            else:
                convergence_time = int(alert_item_data[0].get('convergence_time'))

                old_time = self.send_status_cache[monitor_id]

                if raw_message.get('time') - old_time > convergence_time:
                    logging.debug("message will fresh and send")
                    self.send_message(email_lst, message)
                    self.send_status_cache[monitor_id] = int(time.time())
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
        for _, _email in email_lst:
            self.mail_server.mail_send(_email, message)


if __name__ == '__main__':
    logging.basicConfig(
        # filename=self.config.var_dict.get('logfile') or None,
        level=logging.DEBUG,
        format='%(levelname)s:%(asctime)s:%(message)s'
    )
    logging.info('watcher log init succeed...')

    alert = Alerter()

    job_lst = list()

    t1 = threading.Thread(target=alert.pull_judge_event)
    t1.start()
    job_lst.append(t1)

    for _ in range(2):
        t = threading.Thread(target=alert.alert_main)
        job_lst.append(t)
        t.start()

    for t in job_lst:
        t.join()
