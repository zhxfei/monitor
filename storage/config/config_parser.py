import sys

from common.config.config_parser import ConfigParser


class StorageConfigParser(ConfigParser):
    def config_parse(self):
        for con_n, con_v in self._var_dict.items():
            if isinstance(con_v, dict):
                try:
                    self.var_dict[con_n] = con_v if con_v['enabled'] is True else None
                except KeyError as e:
                    # logging not init
                    print("unsupported config file %s" % e)
                    sys.exit(3)
            else:
                self.var_dict[con_n] = con_v
