import json
import argparse

from flask import Flask, make_response, jsonify
from flask_restful import Api

from api.resources.monitor_data import MonitorData
from api.resources.host_list import HostList, IpList
from api.resources.metric_list import MetricList

app = Flask(__name__)

a = Api(app)

a.add_resource(MonitorData, '/monitor/v1/items')
a.add_resource(HostList, '/monitor/v1/hosts')
a.add_resource(MetricList, '/monitor/v1/metrics')
a.add_resource(IpList, '/monitor/v1/ips')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@a.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data), code)
    resp.headers.extend({
        'Access-Control-Allow-Origin': '*'
    })
    return resp


if __name__ == '__main__':
    description = '''EaseMonitor Restful API design for data search'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-a', '--host',
                        required=True,
                        dest='host',
                        type=str,
                        action='store',
                        help='define Monitor API server host listening')

    parser.add_argument('-p', '--port',
                        required=True,
                        dest='port',
                        type=int,
                        action='store',
                        help='define Monitor API server host listening')

    args = parser.parse_args()
    app.run(args.host, args.port)
