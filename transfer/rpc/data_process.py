# encoding: utf-8
import logging

from gevent.queue import Full

"""
改进： rpc逻辑简化,rpc 服务接收数据,写入本地定长的cache queue,之后worker greenlet 进行数据转发到redis队列
      当后端redis挂掉，本地的内存可以做部分的缓存
"""


def data_process(item_data, cache_queue_map):
    try:
        for _, q in cache_queue_map.items():
            q.put_nowait(item_data)
        return True, 'cache_queue in'
    except Full as e:
        logging.error('queue is full, %s' % e)
        return False, 'queue is full'

    except Exception as e:
        return False, 'Unknown error'
