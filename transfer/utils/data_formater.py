import json
import logging

STANDARD_FORMAT = (
    'tags',
    'value',
    'metrics',
    'counterType',
    'timestamp',
    'step'
)
NOT_FORMAT_INFO = "data contains key not in %s" % "/".join(STANDARD_FORMAT)


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

        for data in data_lst:
            if not isinstance(data, dict):
                raise ValueError("data contains not dict")

            for key in data.keys():
                check_type(key)
    except ValueError as e:
        logging.error("data format check error %s" % e)
        return False, None
    except Exception as e:
        logging.error("data format check unknown error %s" % e)
        return False, None
    else:
        return True, data_lst


def check_type(key):
    if key not in STANDARD_FORMAT:
        raise ValueError(NOT_FORMAT_INFO)
