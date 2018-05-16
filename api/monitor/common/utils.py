from functools import wraps

from bson.errors import InvalidId
from flask_restful import abort
from flask import Response


def invalid_id_check(func):
    @wraps
    def new_func(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
        except InvalidId:
            abort(400, message='invalid id error')
        else:
            return res

    return new_func


def access_control_allow(func):
    @wraps
    def new_func(*args, **kwargs):
        res = func(*args, **kwargs)
        if isinstance(res, Response):
            res.headers.extend({
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,OPTION,DELETE',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization'
            })
        return res

    return new_func
