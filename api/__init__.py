"""
    this module for flask restful app initialization
"""
import json

from flask import Flask, make_response, current_app
from flask_restful import Api

from api.monitor import register_url

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'zh-ss-dxz-zxw'

# restful
api_rest = Api(app)


def db_setup():
    from api.monitor.common.mongo_clt import create_conn
    with app.app_context():
        current_app.mongo_conn = create_conn()


def register_token_and_error():
    from . import token, error_handle


@api_rest.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers)
    resp.headers.extend({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,OPTION,DELETE',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization'
    })
    return resp


register_url(api_rest)
register_token_and_error()
db_setup()
