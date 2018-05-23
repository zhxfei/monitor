import logging

import gevent
from gevent.queue import Full

from watcher.net import DataPuller
from watcher.model import JudgeItemFetcher, gen_key, MonitorItemCacheMap
from watcher.config.default_setting import DEFAULT_PULLER_CONF, JUDGE_URL


class MonitorItemHelper:
    def __init__(self, worker_queue=None):
        self.data_puller = DataPuller.from_config(DEFAULT_PULLER_CONF)
        self.batch = 106
        self._thread_sleep_time = 1
        self.counter = 0
        self.data_cache_map = MonitorItemCacheMap()

        # self._lock = lock
        self.worker_queue = worker_queue

    def push_judge_msg(self, msg, queue_name):
        if self.data_puller.push_data(msg, queue_name):
            logging.debug("push judge message succeed, %s" % str(msg))
        else:
            logging.error("push judge message failed, %s" % str(msg))

    def pull_monitor_item(self, judge_item_pool):
        """
        pull monitor data from redis and filter out item that watcher don't care about
        then push the data in the cache map, the cache is MonitorItemCacheMap, key is hash of item,
        value is monitor item, MonitorItemCacheMap will only retain a few values that were recently push in.
        :param judge_item_pool:
        :return:
        """
        res = self.data_puller.pull_data(self.batch)
        if res is not None:
            queue_is_empty, data_item_lst = res
            if data_item_lst:
                self._data_filter_and_cache(data_item_lst, judge_item_pool)
            if queue_is_empty:
                logging.debug("monitor item puller: redis queue is empty")
                gevent.sleep(self._thread_sleep_time)
        else:
            gevent.sleep(1)

    def _data_filter_and_cache(self, data_item_lst, judge_item_pool):
        """
        the logic which filter data from puller and push in cache
        """
        old_counter = self.counter

        for item_data in data_item_lst:
            key = gen_key(item_data)
            if key in judge_item_pool:
                self.counter += 1
                self.data_cache_map.push(item_data)
                try:
                    self.worker_queue.put_nowait(
                        (key, item_data.get('value'), item_data.get('timestamp'))
                    )
                except Full:
                    logging.error("judge worker queue is full the judge task will be lost")

        if old_counter == self.counter:
            # may api server set no judge police or judge policy fetch failed
            logging.info("no judge item in item judge pool, counter: %d" % self.counter)
            gevent.sleep(1)
        else:
            gevent.sleep(1)

    def get_data_from_cache(self, key, n):
        return self.data_cache_map.get_recent_data(key, n)


class JudgeItemHelper:
    def __init__(self, url=JUDGE_URL):
        self.judge_item_fetcher = JudgeItemFetcher(url)
        self.judge_item_pool = dict()

    def update_pool(self):
        """
        update judge item pool forever
        :return:
        """
        data = self.judge_item_fetcher.get_recent()
        if isinstance(data, list):
            self.judge_item_pool = {hash(item): item for item in data}
            return True
        else:
            logging.error(
                "update pool error: {error}".format(error=str(data) if data is not None else "data is none")
            )
            return False

    def get_item_from_pool(self, key):
        return self.judge_item_pool.get(key)
