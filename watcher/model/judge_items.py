import logging

from .utils import gen_key
from watcher.net import UrlFetcher


class JudgeItem:
    judge_item_cache = dict()
    update_time_cache = dict()

    def __init__(self, **kwargs):
        self.metrics = kwargs.get('metrics')
        self.condition = kwargs.get('condition')
        self.tags = kwargs.get('tags')
        self.monitor_id = kwargs.get('monitor_id')

    def __str__(self):
        return "Judge Item for %s, condition: %s" % (self.metrics, self.condition)

    def __hash__(self):
        _key = gen_key({
            "metrics": self.metrics,
            "tags": self.tags
        })
        return _key

    @classmethod
    def from_cache(cls, params):
        """
            return the judge item instance
        :param params:
        :return:
        """
        key = gen_key(params)
        update_time = params.get('update_time')
        if key in cls.judge_item_cache and cls.update_time_cache[key] == update_time:
            # if the judge_item is in cache and has no update
            return cls.judge_item_cache[key]
        # judge item should new or update and replace the old instance
        instance = cls(**params)
        cls.judge_item_cache[key] = instance
        cls.update_time_cache[key] = update_time
        logging.info("judge item getting new: %s" % instance)
        return cls.judge_item_cache[key]


class JudgeItemFetcher(UrlFetcher):
    def get_recent(self):
        """
        get policy recent instance from api server
        :return:    list(Policy instance) or None or dict
            if return value is None, means requests failed
            if return value is list, means requests succeed, and return response data
            if return value is dict, means requests got an 4** error
        """
        response = self.fetch()

        if response is None:
            return None
        elif response.status_code == 200:
            judge_item_data = response.json()
            judge_item_lst = [JudgeItem.from_cache(instance_data)
                              for instance_data in judge_item_data]
            return judge_item_lst
        else:
            return response.json()

    @classmethod
    def from_config(cls, config):
        """
        get policy fetcher from config
        :param config:
        :return:
        """
        return cls(**config)
