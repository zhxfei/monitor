# from watcher.strategy import policy_cache, strategy_cache
# from pprint import pprint
# from watcher.fetcher.fetch import Fetcher
# from watcher.config.default_setting import API_URL
# from watcher.strategy.policy import Policy
#
# import time
# import threading
#
#
# def cache_print():
#     while True:
#         pprint(policy_cache)
#         pprint(strategy_cache)
#         time.sleep(2)
#         print('-' * 20)
#
#
# def change():
#     fetcher = Fetcher(API_URL + '/policies')
#     res = fetcher.fetch()
#
#     if res.status_code == 200:
#         for data in res.json():
#             Policy.from_dict(data)
#
#
# if __name__ == '__main__':
#     t1 = threading.Thread(target=change)
#     t2 = threading.Thread(target=cache_print)
#
#     t1.start()
#     t2.start()
#
#     t1.join()
#     t2.join()
