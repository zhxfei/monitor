import json
import logging

standard_format = [
    'tags',
    'value',
    'metric',
    'counterType',
    'timestamp',
    'endpoint',
    'step'
]


def check_data_is_format(data):
    try:
        data_lst = data
        if not isinstance(data, list):
            data_lst = json.loads(data)
        for d in data_lst:
            if isinstance(d, dict):
                for key in d.keys():
                    if key not in standard_format:
                        return False, None
            else:
                return False, None
        return True, data_lst
    except Exception as e:
        return False, None


def item_key_gen(item_data):
    info = item_data['tags'] + item_data['endpoint'] + item_data['metric']
    return info
