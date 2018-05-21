from gevent import time

from .utils import gen_key
from .http_client import UrlFetcher


class JudgeItem:
    judge_item_cache = dict()

    def __init__(self, **kwargs):
        self.metrics = kwargs.get('metrics')
        self.condition = kwargs.get('condition')
        self.tags = kwargs.get('tags')
        self.monitor_id = kwargs.get('monitor_id')

    def __str__(self):
        return "Judge Item Structure for %s" % self.metrics

    def __hash__(self):
        _key = gen_key({
            "metrics": self.metrics,
            "tags": self.tags
        })
        return _key

    @classmethod
    def from_cache(cls, params):
        """

        :param params:
        :return:
        """
        key = gen_key(params)

        if key not in cls.judge_item_cache:
            instance = cls(**params)
            cls.judge_item_cache[key] = instance

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
