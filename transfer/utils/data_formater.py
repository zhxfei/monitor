import json
import logging

STANDARD_FORMAT = (
    'tags',
    'value',
    'metric',
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
            assert isinstance(data, dict), ValueError("data contains not dict")

            for key in data.keys():
                assert key in STANDARD_FORMAT, ValueError(NOT_FORMAT_INFO)
    except ValueError as e:
        logging.error("data format check error %s" % e)
        return False, None
    except Exception as e:
        logging.error("data format check unknown error %s" % e)
        return False, None
    else:
        return True, data_lst
