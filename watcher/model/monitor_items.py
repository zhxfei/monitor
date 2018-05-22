import heapq
import logging
from datetime import datetime
from gevent.lock import BoundedSemaphore
from .utils import gen_key

CACHE_LEN = 11


class MonitorItem:
    __slot__ = ('metrics', 'timestamp', 'value')

    def __init__(self, **kwargs):
        self.metrics = kwargs.get('metrics')
        self.timestamp = kwargs.get('timestamp')
        self.value = kwargs.get('value')

    def __repr__(self):
        return "Monitor_item: {} {} {}".format(self.metrics, datetime.fromtimestamp(self.timestamp), self.value)

    def __gt__(self, other):
        return self.timestamp > other.timestamp

    __str__ = __repr__


class MonitorItemHeapQueue:
    def __init__(self):
        self.item_lst = []
        self._lock = BoundedSemaphore(1)

    def insert_item(self, item_instance):
        """
        insert monitor item to heap by timestamp, the item_lst cache the recent MonitorItem instance
        :param item_instance: MonitorItem
        :return:
        """

        if len(self.item_lst) == CACHE_LEN:
            heapq.heappushpop(self.item_lst, (item_instance.timestamp, item_instance))
        else:
            heapq.heappush(self.item_lst, (item_instance.timestamp, item_instance))

    def get_max_n(self, n):
        res = heapq.nlargest(n, self.item_lst)
        return res


class MonitorItemCacheMap:
    def __init__(self):
        self.cache_map = dict()

    def push(self, monitor_item_):
        _monitor_item = MonitorItem(**monitor_item_)
        key = gen_key(monitor_item_)
        if key not in self.cache_map:
            _h = MonitorItemHeapQueue()
            self.cache_map[key] = _h

        self.cache_map[key].insert_item(_monitor_item)

    def get_recent_data(self, key, n):
        """
        get history data from cache
        :param key:  the key of the item map
        :param n:   int : the number of get recent data times
        :return:
        """
        if key not in self.cache_map:
            logging.error("judge item key needed data not in cache")
            return None
        _h = self.cache_map[key]

        if len(_h.item_lst) < int(n):
            logging.error('MonitorItemHeapQueue has no su much cache')
        else:
            return _h.get_max_n(n)


"""
if __name__ == '__main__':


    # heapq test

    import time
    from random import randint

    start_time = time.time()
    monitor_item_heap = MonitorItemHeapQueue()
    for _ in range(500000):
        i = randint(1, 100000)

        item = {'tags': {'host_ip': '10.83.3.48', 'hostname': 'newbie-unknown85824.i.nease.net'},
                'timestamp': i,
                'value': i, 'metrics': 'system.load.1min', 'step': 1, 'counterType': 'GAUGE'}
        monitor_item = MonitorItem(**item)
        monitor_item_heap.insert_item(monitor_item)

        # t = threading.Thread(target=monitor_item_heap.insert_item, args=(monitor_item,))
        # t.setDaemon(True)
        # t.start()
    print(monitor_item_heap.item_lst)
    print(len(monitor_item_heap.item_lst))
    print(monitor_item_heap.get_max_n(5))

    print("COST: {}".format(time.time() - start_time))


"""
