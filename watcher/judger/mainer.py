import logging
from datetime import datetime
from functools import reduce
from collections import namedtuple

import gevent
from gevent.queue import LifoQueue, Empty

from .helper import JudgeItemHelper, MonitorItemHelper
from watcher.config.default_setting import (JUDGE_ITEM_SYNC_INTERVAL,
                                            JUDGE_ITEM_SYNC_FAILED_WAIT,
                                            JUDGE_QUEUE_NAME)

Condition = namedtuple('Condition', ['cmd', 'cmp_times', 'cmp_type', 'cmp_value'])


class Judge:
    def __init__(self):
        self._worker_queue = LifoQueue(maxsize=100000)
        self.monitor_data_helper = MonitorItemHelper(worker_queue=self._worker_queue)

        self.judge_helper = JudgeItemHelper()
        self.judge_running = True

    def pull_monitor_item(self):
        while True:
            self.monitor_data_helper.pull_monitor_item(self.judge_helper.judge_item_pool)

    def sync_judge_item(self):
        while True:
            res = self.judge_helper.update_pool()
            if not res:
                gevent.sleep(JUDGE_ITEM_SYNC_FAILED_WAIT)
            else:
                gevent.sleep(JUDGE_ITEM_SYNC_INTERVAL)

    def _get_recent_monitor_item(self, key, n):
        return self.monitor_data_helper.data_cache_map.get_recent_data(key, n)

    def _get_recent_data(self, key, condition):
        """
        get recent data from data cache map
        :param key: int  the key of monitor item recently
        :param condition:   Condition
        :return:
        """
        times_ = int(condition.cmp_times)
        if condition.cmd == 'diff':
            times_ += 1
        recent_data = self._get_recent_monitor_item(key, times_)
        if recent_data is not None:
            return [data[1] for data in recent_data]

    def _get_judge_item(self):
        return self.judge_helper.judge_item_pool

    def judge_loop(self):
        while True:
            try:
                key, *msg = self._worker_queue.get_nowait()

                # judge item won't be none
                judge_item = self.judge_helper.judge_item_pool.get(key)

                # _judge_main function could contains blocked function call
                # so should create a new greenlet
                gevent.spawn(self._judge_main, key, judge_item, msg)

                gevent.sleep(0)

            except Empty:
                logging.debug("judge worker queue is Empty")
                gevent.sleep(0.1)

    def _judge_handler(self, msg, judge_item):
        message = self._build_judge_msg(msg, judge_item)
        self.monitor_data_helper.data_puller.push_judge_msg(message, JUDGE_QUEUE_NAME)

    def _judge_main(self, key, judge_item, msg):
        try:
            condition = self.condition_resolve(judge_item)
            should_judge = self._judge_process(key, condition)
            if should_judge:
                self._judge_handler(msg, judge_item)
        except ValueError as error_:
            logging.error(error_)
        except Exception as error_:
            logging.error("Unknown error type", error_)
        finally:
            gevent.sleep(0)

    def _judge_process(self, key, condition):
        _func = getattr(self, "_op_" + condition.cmd, None)
        if _func is not None:
            recent_items = self._get_recent_data(key, condition)
            if recent_items:
                return _func(condition, recent_items)
        else:
            logging.error("unsupported condition setting")

    def _op_all(self, condition, recent_items):
        res_ = reduce(lambda x, y: x and y,
                      [self._compare_value(item.value, condition) for item in recent_items])
        return res_

    def _op_min(self, condition, recent_items):
        values = [item.value for item in recent_items]
        res_ = self._compare_value(min(values), condition)
        return res_

    def _op_max(self, condition, recent_items):
        values = [item.value for item in recent_items]
        res_ = self._compare_value(max(values), condition)
        return res_

    def _op_avg(self, condition, recent_items):
        values = [item.value for item in recent_items]
        res_ = self._compare_value(sum(values) // len(values), condition)
        return res_

    def _op_diff(self, condition, recent_items):
        _res_lst = []
        recent_values = [item.value for item in recent_items]
        for i, v in enumerate(recent_values):
            if i == len(recent_values):
                break
            _res_lst.append(self._compare_value(recent_values[i + 1] - v, condition))
        return reduce(lambda x, y: x and y, _res_lst)

    def _compare_value(self, item_value, condition):
        _func = getattr(self, '_op_' + condition.cmp_type, None)
        if _func is not None:
            cmp_res = _func(item_value, condition.cmp_value)
            return cmp_res
        else:
            logging.error("unsupported condition setting")

    @staticmethod
    def _op_lt(value, value_):
        return value < value_

    @staticmethod
    def _op_lte(value, value_):
        return value <= value_

    @staticmethod
    def _op_gt(value, value_):
        return value > value_

    @staticmethod
    def _op_gte(value, value_):
        return value >= value_

    @staticmethod
    def condition_resolve(judge_item):
        def _convert_type(condition_):
            params_lst = condition_.split('#')
            if len(params_lst) != 4:
                raise ValueError("unsupported condition")

            # cmp_times should be int and cmp_value should be float
            params_lst[1] = int(params_lst[1])
            params_lst[3] = float(params_lst[3])
            return params_lst

        res = _convert_type(judge_item.condition)
        condition = Condition(*res)
        return condition

    @staticmethod
    def _build_judge_msg(msg, judge_item):
        msg_ = {
            'monitor_id': judge_item.monitor_id,
            'metrics': judge_item.metrics,
            'tags': judge_item.tags,
            'time': datetime.fromtimestamp(msg[1]),
            'value': msg[0],
            'condition': judge_item.condition,
        }
        return msg_
