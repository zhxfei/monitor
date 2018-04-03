import sys

import transfer.config.default_config as default_config
from common.config.config_parser import ConfigParser
from transfer.receiver.recv_http_server import HTTPServer
from transfer.receiver.recv_rpc_server import RPCServer
from transfer.sender.redis_sender import RedisSender


class TransferConfigParser(ConfigParser):
    def config_parse(self):
        """parse configuration from config file and default config"""
        try:
            self.var_dict = self.get_raw_dict()
            self.receiver_conf_parse()
            self.sender_conf_parse()
            self.router_conf_parse()
        except ValueError as error_info:
            sys.stderr.write(error_info)
            sys.exit(3)

    def sender_conf_parse(self):
        sender_conf = self.get_dict('sender')
        for backend_type, params in sender_conf.items():
            if not isinstance(params, dict):
                return
            sender_default_conf = default_config.DEFAULT_SENDER_CONF.copy()
            params['backend_type'] = backend_type
            sender_default_conf.update(params)
            self.var_dict[backend_type] = sender_default_conf

    def router_conf_parse(self):
        router_default_conf = default_config.DEFAULT_ROUTER_CONF.copy()
        router_conf = self.get_dict('router')
        router_conf.update(router_default_conf)
        self.var_dict['router'] = router_default_conf

    def receiver_conf_parse(self):
        http_server_params = default_config.DEFAULT_HTTP_CONF.copy()
        rpc_server_params = default_config.DEFAULT_RPC_SERVER_CONF.copy()
        receiver_params = self.get_dict('receiver')

        try:
            if receiver_params['http'].pop('enabled') is True:
                http_server_params.update(receiver_params['http'])
            else:
                http_server_params = None
            self.var_dict['http'] = http_server_params
        except (KeyError, AttributeError) as error_info:
            self.var_dict['http'] = None
            sys.stderr.write(error_info)

        try:
            if receiver_params['rpc'].pop('enabled') is True:
                rpc_server_params.update(receiver_params['rpc'])
            else:
                rpc_server_params = None
            self.var_dict['rpc'] = rpc_server_params
        except (KeyError, AttributeError) as error_info:
            self.var_dict['rpc'] = None
            sys.stderr.write(error_info)

    def get_http_from_config(self, cache_queue_map):
        """ get http server from config """
        if self.var_dict['http'] is not None:
            self.var_dict['http']['cache_queue_map'] = cache_queue_map
            return HTTPServer.from_config(self.var_dict['http'])

    def get_rpc_from_config(self, cache_queue_map):
        """ get rpc server from config """
        if self.var_dict['rpc'] is not None:
            self.var_dict['rpc']['cache_queue_map'] = cache_queue_map
            return RPCServer.from_config(self.var_dict['rpc'])

    def get_sender_from_config(self, backend_type):
        config = self.var_dict[backend_type]
        if isinstance(config, dict):
            queue_type = config['queue'].pop('type')
            if queue_type == default_config.SENDER_TYPE_REDIS:
                return RedisSender.from_config(config)
