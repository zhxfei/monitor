import logging
from ast import literal_eval

from flask import Flask, request, jsonify, current_app
from gevent.pywsgi import WSGIServer

from transfer.receiver.data_process import data_process
from transfer.utils.data_formater import check_data_is_format

data_app = Flask(__name__)


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
            for item_data in data_lst:
                # for data process

                # get key from item_data
                with data_app.app_context():
                    status, reason = data_process(item_data, current_app.cache_queue_map)

                    if status:
                        res['ok'] = True
                    else:
                        res['ok'] = False
                        res['msg'] += reason
            logging.debug('http server receiver succeed: %s' % res['msg'])
            return jsonify(res), 200
        else:
            res = {'ok': False, 'msg': 'Unsupported Data Format'}
            logging.info('http server receiver error: %s' % res['msg'])
            return jsonify(res), 400
    except Exception as e:
        res = {'ok': False, 'msg': 'Unknown Error'}
        logging.info('http server receiver error: %s' % e)
        return jsonify(res), 401


class HttpServer:
    def __init__(self, http_host=None, http_port=None, cache_queue_map=None):
        self.http_host = http_host or 'localhost'
        self.http_port = http_port or 8080

        global data_app
        with data_app.app_context():
            current_app.cache_queue_map = cache_queue_map or None
        self.server = WSGIServer((self.http_host, self.http_port), data_app)

    def serve_forever(self):
        try:
            logging.info("HTTP-server(Common API) will running at %s:%d" % (self.http_host,
                                                                            self.http_port))
            self.server.serve_forever()
        except Exception as e:
            logging.error("HTTP-server(Common API) run error")
            logging.error(e)
