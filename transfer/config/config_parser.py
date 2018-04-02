import sys

import transfer.config.default_config as default_config
from common.config.config_parser import ConfigParser
from transfer.receiver.recv_http_server import HTTPServer
from transfer.receiver.recv_rpc_server import RPCServer


class TransferConfigParser(ConfigParser):
    def config_parse(self):
        """parse configuration from config file and default config"""
        self.receiver_conf_parse()
        self.sender_conf_parse()
        self.router_conf_parse()

    def sender_conf_parse(self):
        pass

    def router_conf_parse(self):
        pass

    def receiver_conf_parse(self):
        http_server_params = default_config.DEFAULT_HTTP_CONF.copy()
        rpc_server_params = default_config.DEFAULT_RPC_SERVER_CONF.copy()
        receiver_params = self.get_dict('receiver')
        self.var_dict = self.get_raw_dict()

        try:
            if receiver_params['http'].pop('enabled') is True:
                http_server_params.update(receiver_params['http'])
            else:
                http_server_params = None
            self.var_dict['http'] = http_server_params
        except (ValueError, AttributeError) as error_info:
            self.var_dict['http'] = None
            sys.stderr.write(error_info)

        try:
            if receiver_params['rpc'].pop('enabled') is True:
                rpc_server_params.update(receiver_params['rpc'])
            else:
                rpc_server_params = None
            self.var_dict['rpc'] = rpc_server_params
        except (ValueError, AttributeError) as error_info:
            self.var_dict['rpc'] = None
            sys.stderr.write(error_info)

    def get_http_from_config(self, cache_queue_map):
        """ get http server from config """
        if self.var_dict['http'] is not None:
            self.var_dict['http']['cache_queue_map'] = cache_queue_map
            return HTTPServer.from_config(self.var_dict['http'])

    def get_sender_from_config(self, cache_queue_map):
        """ get rpc server from config """
        if self.var_dict['rpc'] is not None:
            self.var_dict['rpc']['cache_queue_map'] = cache_queue_map
            return RPCServer.from_config(self.var_dict['rpc'])
