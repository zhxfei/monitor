import logging

import gevent

from common.queue.exceptions import QueueFullException


def send_to_backend(redis_q, cache_q, sender_wait_time, sender_retry_times):
    while not cache_q.empty():
        data = cache_q.get_nowait()
        try:
            redis_q.put(data)
        except QueueFullException:
            status = retry_send_data(redis_q, data, sender_wait_time, sender_retry_times)
            # after retry send, data will be drop or re cache
            if not status:
                # if not cache_q.full():
                #     cache_q.put_nowait(data)
                #     return
                # else:
                # # error count
                logging.debug("%s resend failed" % str(data))
            logging.debug("%s resend succeed" % str(data))
    return


def retry_send_data(redis_q, data, wait_time, retry_times):
    logging.debug('%s will be resend %d times' % (str(data), retry_times))
    count = 0
    while count < retry_times:
        try:
            gevent.sleep(wait_time)
            redis_q.put(data)
            return True
        except QueueFullException as e:
            logging.debug("%s , %s send retry %d" % (e, str(data), count))
            count += 1
    return False
