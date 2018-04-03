import logging
from ast import literal_eval

from flask import Flask, request, jsonify, current_app
from gevent.pywsgi import WSGIServer

from transfer.receiver.data_process import data_process
from transfer.utils.data_formater import check_data_is_format

data_app = Flask(__name__)

STATUS_OK = 200
STATUS_NOT_FORMAT = 400
STATUS_UNKNOWN_ERROR = 401


@data_app.route('/v1/data_push', methods=['POST'])
def data_upload():
    try:
        item_data = request.data
        if isinstance(item_data, bytes):
            item_data = item_data.decode('utf-8')

        item_data = literal_eval(item_data)
        if isinstance(item_data, dict):
            item_data = [item_data]

        data_is_format, data_lst = check_data_is_format(item_data)

        res = {
            'ok': None,
            'msg': ''
        }

        if data_is_format:
            with data_app.app_context():
                for item_data in data_lst:
                    status, reason = data_process(item_data, current_app.cache_queue_map)

                    if status:
                        res['ok'] = True
                    else:
                        res['ok'] = False
                        res['msg'] += reason
            logging.debug('http server receiver succeed: %s' % res['msg'])
            return jsonify(res), STATUS_OK
        else:
            res = {'ok': False, 'msg': 'Unsupported Data Format'}
            logging.info('http server receiver error: %s' % res['msg'])
            return jsonify(res), STATUS_NOT_FORMAT
    except Exception as e:
        res = {'ok': False, 'msg': 'Unknown Error'}
        logging.info('http server receiver error: %s' % e)
        return jsonify(res), STATUS_UNKNOWN_ERROR


class BaseServer:
    """Base server class for http server and rpc server """

    def __init__(self, host=None, port=None, cache_queue_map=None):
        self.host = host
        self.port = port
        self.cache_queue_map = cache_queue_map
        self.server = self.server_setup()

    def server_setup(self):
        """ abstract method for server setup"""
        raise NotImplementedError

    def serve_forever(self):
        """ abstract method for server start serve loop"""
        raise NotImplementedError


class HTTPServer(BaseServer):
    def server_setup(self):
        """ HTTP server setup"""
        global data_app
        with data_app.app_context():
            current_app.cache_queue_map = self.cache_queue_map
        server = WSGIServer((self.host, self.port), data_app)
        return server

    def serve_forever(self):
        """ HTTP server start serve loop """
        try:
            logging.info("HTTP-server(Common API) binding at %s:%d" % (self.host, self.port))
            self.server.serve_forever()
        except Exception as error_info:
            logging.error("HTTP-server(Common API) run error")
            logging.error(error_info)

    @classmethod
    def from_config(cls, config):
        """
        get http server instance from config
        :param config: dict
        :return: HTTPServer

        """
        return cls(**config)
