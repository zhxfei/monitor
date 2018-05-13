"""
    this module for flask restful app initialization
"""
import json

from flask import Flask, make_response, jsonify, current_app
from flask_restful import Api

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'zh-ss-dxz-zxw'

# restful
api_rest = Api(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found' + str(error)}), 404)


@api_rest.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers or {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,OPTION,DELETE',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization'
    })
    return resp


def register_url():
    from api.monitor.resources.host_list import HostList, IpList
    from api.monitor.resources.metric_list import MetricList
    from api.monitor.resources.monitor_data import MonitorData
    from api.monitor.resources.user import User, UserList
    from api.monitor.common.mongo_clt import create_conn

    global api_rest
    api_rest.add_resource(MonitorData, '/monitor/v1/items')
    api_rest.add_resource(HostList, '/monitor/v1/hosts')
    api_rest.add_resource(MetricList, '/monitor/v1/metrics')
    api_rest.add_resource(IpList, '/monitor/v1/ips')
    api_rest.add_resource(User, '/monitor/v1/user/<string:user_id>')
    api_rest.add_resource(UserList, '/monitor/v1/users')

    from . import token


def db_setup():
    from api.monitor.common.mongo_clt import create_conn
    with app.app_context():
        current_app.mongo_conn = create_conn()


register_url()
db_setup()
