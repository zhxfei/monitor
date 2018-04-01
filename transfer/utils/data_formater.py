import json
import logging

standard_format = [
    'tags',
    'value',
    'metric',
    'counterType',
    'timestamp',
    'step'
]


def check_data_is_format(data):
    """
    check data is format
    :param data:
    :return: format_status, data
    """
    try:
        data_lst = data
        if not isinstance(data, list):
            data_lst = json.loads(data)

        for d in data_lst:
            assert isinstance(d, dict), ValueError("data contains not dict")

            for key in d.keys():
                assert key in standard_format, ValueError(
                    "data contains key not in %s" % "/".join(standard_format))

        return True, data_lst

    except ValueError as e:
        logging.error("data format check error %s" % e)
        return False, None
    except Exception as e:
        logging.error("data format check unknown error %s" % e)
        return False, None


def item_key_gen(item_data):
    info = item_data['tags'] + item_data['endpoint'] + item_data['metric']
    return info
