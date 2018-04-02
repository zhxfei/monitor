import json
import sys


class ConfigParser:
    def __init__(self, config_path):
        self._file_path = config_path
        self._var_dict = {}
        self.var_dict = {}
        self._config_read()
        self.config_parse()

    def _config_read(self):
        try:
            with open(self._file_path, 'r') as f:
                content = f.read()
                self._var_dict.update(json.loads(content))
        except Exception as e:
            sys.stderr.write("Config Write Error: %s" % e)
            sys.exit(4)

    def get_dict(self, attr):
        """ get config from config file which type is a dict"""
        r = self._var_dict.get(attr)
        if not isinstance(r, dict):
            raise ValueError("Not format configuration file")
        return r

    def get_raw_dict(self):
        """ get raw config from config file except dict type"""
        no_dict_conf = {conf_key: conf_value for conf_key, conf_value in self._var_dict.items()
                        if not isinstance(conf_value, dict)}
        return no_dict_conf

    def config_parse(self):
        raise NotImplementedError
