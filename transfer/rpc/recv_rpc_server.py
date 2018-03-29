import json
import logging

import zerorpc
from .data_process import data_process
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

                status, reason = data_process(item_data,
                                              self.cache_queue_map)

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


class MonitorRpcServer:
    def __init__(self, listen, cache_queue_map):
        self.rpc_listen = "tcp://" + listen
        self.cache_queue_map = cache_queue_map

    def server_forever(self):
        try:
            s = zerorpc.Server(UploadDataModule(cache_queue_map=self.cache_queue_map))
            s.bind(self.rpc_listen)
            logging.info('RPC-server will running ')
            s.run()
        except Exception as e:
            logging.error('RPC-server run error')
