from gevent import monkey

monkey.patch_all()

import time
import gevent
from gevent.queue import Queue
import requests

q = Queue()


def producer():
    for x in range(10000000):
        # print("put {} in queue".format(x))
        q.put_nowait(x)

        if x % 5 == 0:
            gevent.sleep(0)


def consumer():
    for _ in range(10000000):
        # print("pop {} out queue".format(_))
        x = q.get_nowait()
        # print(x)

        if x % 5 == 0:
            gevent.sleep(0)


def crawl():
    for _ in range(20):
        t1 = time.time()
        url = "http://www.baidu.com"
        print("crawl {}".format(_))
        res = requests.get(url)
        print(time.time() - t1)
        print(res)
        gevent.sleep(1)
        print(time.time() - t1)


job_lst = list()
job_lst.append(gevent.spawn(crawl))
job_lst.append(gevent.spawn(producer))
job_lst.append(gevent.spawn(consumer))

gevent.joinall(job_lst)
