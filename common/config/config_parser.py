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
            sys.stderr.write("config write error: %s" % e)
            print(e)
            sys.exit(4)

    def config_parse(self):
        raise NotImplementedError
