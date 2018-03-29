import json
import sys


class TransferConfigParser:
    def __init__(self, config_path):
        self._file_path = config_path
        self._var_dict = {}
        self.var_dict = {}
        self.config_parse()

    def config_parse(self):
        with open(self._file_path, 'r') as f:
            content = f.read()
            self._var_dict.update(json.loads(content))

        self._config_parse()

    def _config_parse(self):
        for con_n, con_v in self._var_dict.items():
            if isinstance(con_v, dict):
                try:
                    self.var_dict[con_n] = con_v if con_v['enabled'] is True else None
                except Exception as e:
                    # logging do not init
                    print("unsupported config: %s" % e)
                    sys.exit(3)
            else:
                self.var_dict[con_n] = con_v
