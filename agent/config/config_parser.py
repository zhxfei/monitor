import sys

import agent.config.default_config as default_config
from agent.collect.collector import PsUtilsCollector
from agent.sender.rpc_client_sender import AgentRPCClient
from common.config.config_parser import ConfigParser


class AgentConfigParser(ConfigParser):
    """
        read configuration from config file and default config for Agent
        get data sender and data collector
    """
    def config_parse(self):
        """parse configuration from config file and default config"""
        self.var_dict = self.get_raw_dict()

        collector_params = default_config.COLLECTOR_DEFAULT_CONF.copy()
        transfer_params = default_config.TRANSFER_DEFAULT_CONF.copy()
        try:
            collector_params.update(self.get_dict('collector'))
            transfer_params.update(self.get_dict('transfer'))
        except ValueError as error_info:
            sys.stderr.write(error_info)
        else:
            self.var_dict['collector'] = collector_params
            self.var_dict['transfer'] = transfer_params

    def get_collector_from_config(self):
        """ get collector from config """
        return PsUtilsCollector.from_config(self.var_dict['collector'])

    def get_sender_from_config(self):
        """ get sender from config """
        return AgentRPCClient.from_config(self.var_dict['transfer'])
