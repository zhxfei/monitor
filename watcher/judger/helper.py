import logging
from gevent import time

from watcher.model import JudgeItemFetcher, gen_key, DataPuller, MonitorItemCacheMap
from watcher.config.default_setting import DEFAULT_PULLER_CONF, API_URL

JUDGE_URL = API_URL + "/judge_items"


class MonitorItemHelper:
    def __init__(self):
        self.data_puller = DataPuller.from_config(DEFAULT_PULLER_CONF)
        self.batch = 106
        self.thread_sleep_time = 1
        self.counter = 0
        self.data_cache_map = MonitorItemCacheMap()

    def pull_monitor_item(self, judge_item_pool):
        """
        pull monitor data from redis and filter out item that watcher don't care about
        then push the data in the cache map, the cache is MonitorItemCacheMap, key is hash of item,
        value is monitor item, MonitorItemCacheMap will only retain a few values that were recently push in.
        :param judge_item_pool:
        :return:
        """
        queue_is_empty, data_item_lst = self.data_puller.pull_data(self.batch)
        if data_item_lst:
            self._data_filter_and_cache(data_item_lst, judge_item_pool)
        if queue_is_empty:
            logging.debug("Queue is empty")
            time.sleep(self.thread_sleep_time)

    def _data_filter_and_cache(self, data_item_lst, judge_item_pool):
        """
        filter data from puller and push in queue logic
        """
        old_counter = self.counter

        for item in data_item_lst:
            key = gen_key(item)
            if key in judge_item_pool:
                self.counter += 1
                print(True)
                self.data_cache_map.push(item)
                import time as time_
                print("COST: ", time_.time()-item.get('timestamp'))

        if old_counter == self.counter:
            # may judge police is null or judge policy fetch failed
            logging.info("no judge item in item judge pool, counter: " % self.counter)
            time.sleep(1)

        # for item in data_item_lst:
        #     self.data_cache_map.push(item)
        #
        # print(self.data_cache_map.cache_map)
        # print("cache queue length: {}".format(len(self.data_cache_map.cache_map)))


class JudgeItemHelper:
    def __init__(self):
        self.judge_item_fetcher = JudgeItemFetcher(JUDGE_URL)
        self.judge_item_pool = dict()

    def update_pool(self):
        """
        update judge item pool forever
        :return:
        """
        data = self.judge_item_fetcher.get_recent()
        if isinstance(data, list):
            self.judge_item_pool = {hash(item): item for item in data}
            logging.info("judge item getting new: %s" % self.judge_item_pool)
            return True
        else:
            logging.error(
                "update pool error: {error}".format(error=str(data) if data is not None else "data is none")
            )
            return False
