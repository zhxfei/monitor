from gevent import monkey
monkey.patch_all()

import logging

import requests
from requests.auth import HTTPBasicAuth

from watcher.config.default_setting import DEFAULT_AUTH

ALLOW_HTTP_METHOD = ('get', 'post', 'options', 'delete', 'put')


class UrlFetcher:
    """
        Fetcher is class for get data from api server
    """
    request_params = {
        'auth': HTTPBasicAuth(*DEFAULT_AUTH),
        # 'timeout': 3
    }

    def __init__(self, url, retry_time=3, method='get', data=None):
        self.url = url
        self.data = data
        self.retry_time = retry_time

        assert method in ALLOW_HTTP_METHOD, ValueError('method not in %s' % "/".join(ALLOW_HTTP_METHOD))
        self.method = method
        self._prepare_requester()
        self.requester = self._get_request()

    def fetch(self, url=None):
        """
         fetch data from instance url; try some time and get data from url
        :return: requests.Response
        """
        count = 0
        result = None

        while count < self.retry_time:
            result = self._get_response(url)
            if result is not None:
                break
            else:
                count += 1
        return result

    def _prepare_requester(self):
        """
        prepare request data, if method is 'get', request data should encode into url
        if method is 'post' or other, request data could taken by form or other
        """
        if self.method == 'get':
            self.request_params.setdefault('params', self.data)
        else:
            self.request_params.setdefault('data', self.data)

    def _get_request(self):
        """
        get requester from self.method
        :return: requests.Request
        """
        return getattr(requests, self.method)

    def _get_response(self, url):
        try:
            response = self.requester(url or self.url,
                                      **self.request_params)
            return response
        except requests.exceptions.RequestException as e:
            logging.error("requests error: {}".format(e))
            return
        except Exception as e:
            logging.error("unknown error".format(e))
            return