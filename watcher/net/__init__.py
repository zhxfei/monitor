from gevent import monkey

monkey.patch_all()

from .http_client import UrlFetcher
from .data_puller import DataPuller