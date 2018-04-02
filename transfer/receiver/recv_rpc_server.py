import json
import logging

import zerorpc

from transfer.receiver.recv_http_server import BaseServer
from transfer.receiver.data_process import data_process
from transfer.utils.data_formater import check_data_is_format


class UploadDataModule:
    def __init__(self, cache_queue_map):
        self.cache_queue_map = cache_queue_map

    def upload_data(self, data):
        is_format, data_lst = check_data_is_format(data)
        res = {
            'ok': None,
            'msg': ''
        }
        if is_format:
            for item_data in data_lst:
                # for data process
                status, reason = data_process(item_data, self.cache_queue_map)

                if status:
                    res['ok'] = True
                    logging.debug('RPC server receive data succeed: %s' % res['msg'])
                else:
                    res['ok'] = False
                    res['msg'] += reason
                    logging.info('RPC server receive data failed: %s' % res['msg'])
            return json.dumps(res)
        else:
            res['ok'] = False
            res['msg'] = 'Unsupported Data Format'
            logging.info('RPC server receive data failed: %s' % res['msg'])
            return json.dumps(res)


class RPCServer(BaseServer):
    def server_setup(self):
        listen = "tcp://%s:%d" % (self.host, self.port)
        server = zerorpc.Server(UploadDataModule(cache_queue_map=self.cache_queue_map))
        server.bind(listen)
        logging.info('RPC-server binding at %s' % listen)
        return server

    def serve_forever(self):
        try:
            self.server.run()
        except Exception as error_info:
            logging.error('RPC-server run error')
            logging.error(error_info)

    @classmethod
    def from_config(cls, config):
        return cls(**config)
