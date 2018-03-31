import json
import sys


class AgentConfigParser:
    def __init__(self, config_path):
        self._file_path = config_path
        self._var_dict = {}
        self.var_dict = {}
        self.config_parse()

    def config_parse(self):
        try:
            with open(self._file_path, 'r') as f:
                content = f.read()
                self._var_dict.update(json.loads(content))

            self._config_parse()
        except Exception as e:
            print(e)
            sys.exit(3)

    def _config_parse(self):
        for con_n, con_v in self._var_dict.items():
            if con_n == 'ignore':
                ignore_item_list = [ignore_item for ignore_item, ignore_stat in con_v.items()
                                    if ignore_stat is True]
                self.var_dict['ignore'] = ignore_item_list
            elif con_n == 'transfer' and con_v.get('enabled'):
                self.var_dict['transfer_addr'] = con_v.get('addr')
                self.var_dict['transfer_timeout'] = con_v.get('timeout')
                self.var_dict['transfer_headbeat'] = con_v.get('headbeat')
                self.var_dict['collect_interval'] = con_v.get('interval')
            else:
                self.var_dict[con_n] = con_v
