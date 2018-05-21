import logging
from collections import namedtuple

from gevent import time
from gevent.event import AsyncResult

from .helper import JudgeItemHelper, MonitorItemHelper


class JudgeEventError(Exception):
    pass


JUDGE_ITEM_SYNC_INTERVAL = 3
JUDGE_ITEM_SYNC_FAILED_WAIT = 10
JUDGE_MIN_INTERVAL = 1

Condition = namedtuple('Condition', ['cmd', 'cmp_times', 'cmp_type', 'cmp_value'])


class Judge:
    def __init__(self):
        self.data_helper = MonitorItemHelper()
        self.judge_helper = JudgeItemHelper()

        self._event = AsyncResult()
        self.judge_running = True

    def pull_monitor_item(self):
        while True:
            self.data_helper.pull_monitor_item(self.judge_helper.judge_item_pool)

    def sync_judge_item(self):
        while True:
            res = self.judge_helper.update_pool()
            if not res:
                time.sleep(JUDGE_ITEM_SYNC_FAILED_WAIT)
            else:
                time.sleep(JUDGE_ITEM_SYNC_INTERVAL)

    def get_recent_monitor_item(self, key, n):
        return self.data_helper.data_cache_map.get_recent_data(key, n)

    def judge_loop(self):
        while self.judge_running:
            if len(self.judge_helper.judge_item_pool) > 0:
                for key, judge_item in self.judge_helper.judge_item_pool.items():
                    self._judge_main(key, judge_item)

                # if not sleep, the greenlet will run forever
                # fix: JUDGE_MIN_INTERVAL will cause a lot of repeated judge
                time.sleep(JUDGE_MIN_INTERVAL)
            else:
                time.sleep(0.1)

    def _judge_main(self, key, judge_item):

        condition = Condition(*judge_item.condition.split("#"))
        print(condition)
        recent_data = None
        try:
            recent_data = self.get_recent_monitor_item(key, int(condition.cmp_times))
        except ValueError as error_:
            logging.error(error_)
        finally:
            if recent_data is None:
                time.sleep(1)
            else:
                self.process_by_cmd(recent_data)

    @staticmethod
    def process_by_cmd(recent_data):
        # cmp_value = None
        # if cmd_ == 'all':
        #     # cmp_value = (min(recent_data), max(recent_data))
        #     cmp_value = recent_data
        # elif cmd_ == 'avg':
        #     cmp_average()
        # elif cmd_ == 'max':
        #     cmp_max()
        # elif cmd_ == 'min'
        #     cmp_min()
        print("judge main")
        print(recent_data)

    @staticmethod
    def condition_resolve(condition):
        pass
