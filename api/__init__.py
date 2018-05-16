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


def register_url():
    from . import token

    from api.monitor.resources.host_list import HostList, IpList
    from api.monitor.resources.metric_list import MetricList
    from api.monitor.resources.data import MonitorData
    from api.monitor.resources.user import User, UserList
    from api.monitor.resources.strategies import StrategyList, Strategy
    from api.monitor.resources.alerter import Alert, Alerts
    from api.monitor.resources.policy import Policy, PolicyList

    global api_rest
    api_rest.add_resource(MonitorData, '/monitor/v1/items')
    api_rest.add_resource(HostList, '/monitor/v1/hosts')
    api_rest.add_resource(MetricList, '/monitor/v1/metrics')
    api_rest.add_resource(IpList, '/monitor/v1/ips')
    api_rest.add_resource(User, '/monitor/v1/user/<string:user_id>')
    api_rest.add_resource(UserList, '/monitor/v1/users')
    api_rest.add_resource(StrategyList, '/monitor/v1/strategies')
    api_rest.add_resource(Strategy, '/monitor/v1/strategy/<string:strategy_id>')
    api_rest.add_resource(Alert, '/monitor/v1/alert/<string:alert_id>')
    api_rest.add_resource(Alerts, '/monitor/v1/alerts')
    api_rest.add_resource(Policy, '/monitor/v1/policy/<string:monitor_id>')
    api_rest.add_resource(PolicyList, '/monitor/v1/policies')


def db_setup():
    from api.monitor.common.mongo_clt import create_conn
    with app.app_context():
        current_app.mongo_conn = create_conn()


@app.errorhandler(404)
def not_found(error):
    resp = make_response(jsonify({'error': str(error)}), 404)
    resp.headers.extend({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,OPTION,DELETE',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization'
    })
    print(resp.headers)
    return resp


@app.errorhandler(400)
def not_found(error):
    resp = make_response(jsonify({'error': str(error)}), 400)
    resp.headers.extend({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,OPTION,DELETE',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization'
    })
    return resp


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


register_url()
db_setup()
