import sys

import storage.config.default_config as default_config
from common.connections.mongo_conn import MONGOClient
from storage.puller.data_puller import DataPuller
from common.config.config_parser import ConfigParser


class StorageConfigParser(ConfigParser):
    def config_parse(self):
        """parse configuration from config file and default config"""
        self.var_dict = self.get_raw_dict()

        puller_params = default_config.DEFAULT_PULLER_CONF.copy()
        db_params = default_config.DEFAULT_DB_CONF.copy()
        try:
            puller_params.update(self.get_dict('puller'))
            db_params.update(self.get_dict('database'))
        except ValueError as error_info:
            sys.stderr.write(error_info)
        else:
            self.var_dict['puller'] = puller_params
            self.var_dict['database'] = db_params

    def get_db_from_config(self):
        """ get database connection instance from config"""
        database_config = self.var_dict['database']
        database_type = database_config.pop('type')

        if database_type == default_config.DEFAULT_DATABASE_TYPE:
            # get database from  type
            return MONGOClient.from_config(database_config)

    def get_puller_from_config(self):
        """ get puller instance from configuration """
        puller_config = self.var_dict['puller']
        puller_type = puller_config['connection_params'].pop('type')

        if puller_type == default_config.DEFAULT_PULLER_TYPE:
            # get puller from  type
            return DataPuller.from_config(puller_config)


