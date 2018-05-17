from datetime import datetime

from flask_restful import Resource, reqparse, abort
from flask import jsonify, current_app, g
from bson.objectid import ObjectId
from bson.errors import InvalidId

from api import app
from api.security import auth


class AlarmList(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        with app.app_context():
            self.document = current_app.mongo_conn.document_new('monitor_alarm')

        self.post_parser = reqparse.RequestParser()

        self.post_parser.add_argument(
            'policy_id',
            dest='policy_id',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='policy_id not null',
        )
        self.post_parser.add_argument(
            'strategy_id',
            dest='strategy_id',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='strategy_id not null',
        )
        self.post_parser.add_argument(
            'state',
            dest='state',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='alarm state not null',
        )
        self.post_parser.add_argument(
            'create_time',
            dest='create_time',
            type=int,
            location=['json', 'args', 'form'],
            required=False,
            default=int(datetime.now().timestamp()),
        )

    def get(self):
        res = []
        login_user = g.user['login_name']
        alarm_lst = self.document.find({})
        for alarm in alarm_lst:
            if login_user in alarm['owner']:
                alarm_id = str(alarm.pop('_id'))
                alarm['alarm_id'] = alarm_id
                res.append(alarm)
        return res

    def options(self):
        return {'code': 1}

    def post(self):
        args = self.post_parser.parse_args()

        res = self.document.insert_one({
            'policy_id': args.policy_id,
            'strategy_id': args.strategy_id,
            'state': args.state,
            'owner': [g.user['login_name'], ],  # owner is a user list
            'creator': g.user['login_name'],
            'create_time': args.create_time
        })
        return {'_id': str(res.inserted_id)}


class Alarm(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        with app.app_context():
            self.document = current_app.mongo_conn.document_new('monitor_alarm')

        self.put_parser = reqparse.RequestParser()
        self.put_parser.add_argument(
            'state',
            dest='state',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='alarm state not null',
        )
        self.put_parser.add_argument(
            'update_time',
            dest='update_time',
            type=int,
            location=['json', 'args', 'form'],
            required=False,
            default=int(datetime.now().timestamp()),
        )

    def get(self, alarm_id):
        try:
            if alarm_id:
                res = self.document.find_one({
                    '_id': ObjectId(alarm_id)
                }, {'_id': 0})
            else:
                res = None
            if res:
                return jsonify(res)
            else:
                # alert not exists
                abort(404, message='alarm_id not exists')
        except InvalidId:
            abort(400, messgae='no allowed alarm id')

    def delete(self, alarm_id):
        try:
            res = self.document.delete_one({'_id': ObjectId(alarm_id)})
            if res.raw_result['n'] > 0:
                res = {'msg': 'delete succeed'}
            else:
                res = {'msg': 'delete failed'}
            return res
        except InvalidId:
            abort(400, messgae='no allowed alarm id')

    def options(self, alarm_id):
        res = {'ok': True}
        return res

    def put(self, alarm_id):
        args = self.put_parser.parse_args()
        try:
            res = self.document.find_one_and_update(
                {
                    '_id': ObjectId(alarm_id),
                },
                {
                    '$set': {
                        'state': args.state,
                        'update_time': args.update_time,
                    }
                })
            if not isinstance(res, dict):
                abort(404, message='alarm not exists')
            return {'ok': True}
        except InvalidId:
            abort(400, message='no allowed alarm id')
