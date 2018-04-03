"""
this module for data process
"""

import logging

from gevent.queue import Full

QUEUE_FULL_MESSAGE = 'queue is full'
QUEUE_IN_MESSAGE = "push data in queue succeed"


def data_process(item_data, cache_queue_map):
    """
    process data in http server and rpc server
    :param item_data: dict
            monitor item data from agent upload
    :param cache_queue_map: dict
            a dict with backend_type and cache_queue (because every backend has a cache queue)
    :return: tuple
            The action (push in queue) status and some message info
    """
    try:
        for _, queue in cache_queue_map.items():
            queue.put_nowait(item_data)
    except Full as error_info:
        logging.error('queue is full, %s' % error_info)
        return False, QUEUE_FULL_MESSAGE
    else:
        return True, QUEUE_IN_MESSAGE
