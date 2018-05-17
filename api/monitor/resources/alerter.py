from datetime import datetime

from flask_restful import Resource, reqparse, abort
from flask import jsonify, current_app, g, request
from bson.objectid import ObjectId
from bson.errors import InvalidId

from api import app
from api.security import auth
from api.monitor.common.utils import invalid_id_check


class Alerts(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        with app.app_context():
            self.document = current_app.mongo_conn.document_new('monitor_alert')

        self.post_parser = reqparse.RequestParser()

        self.post_parser.add_argument(
            'name',
            dest='name',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='alert name not null',
        )
        self.post_parser.add_argument(
            'type',
            dest='type',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='alert type not null',
        )
        self.post_parser.add_argument(
            'to_persons',
            dest='to_persons',
            type=list,
            location=['json', 'args', 'form'],
            required=True,
            help='alter to persons not null',
        )

    def get(self):
        res = []
        login_user = g.user['login_name']
        alerter_lst = self.document.find({})
        for alerter in alerter_lst:
            if login_user in alerter['owner']:
                alerter_id = str(alerter.pop('_id'))
                alerter['alerter_id'] = alerter_id
                res.append(alerter)
        return res

    def options(self):
        return {'code': 1}

    def post(self):
        args = self.post_parser.parse_args()

        if request.json is not None:
            to_persons = request.json['to_persons']
        else:
            to_persons = request.form['to_persons']
        res = self.document.find_one({
            'name': args.name
        })
        if res is None:
            res = self.document.insert_one({
                'name': args.name,
                'type': args.type,
                # 'tags': args.tags,
                'to_persons': to_persons or args.to_persons,
                'owner': [g.user['login_name'], ],  # owner is a user list
                'creator': g.user['login_name'],
                'update_time': int(datetime.now().timestamp())
            })
            return {'_id': str(res.inserted_id)}
        else:
            # user exists
            abort(400, message="alert name {} has exist".format(args.name))


class Alert(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        with app.app_context():
            self.document = current_app.mongo_conn.document_new('monitor_alert')

        self.put_parser = reqparse.RequestParser()
        self.put_parser.add_argument(
            'name',
            dest='name',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='alert name not null',
        )
        self.put_parser.add_argument(
            'type',
            dest='type',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='alert type not null',
        )
        self.put_parser.add_argument(
            'to_persons',
            dest='to_persons',
            type=list,
            location=['json', 'args', 'form'],
            required=True,
            help='alert to persons not null',
        )

    def get(self, alert_id):
        if alert_id:
            res = self.document.find_one({
                '_id': ObjectId(alert_id)
            }, {'_id': 0})
        else:
            res = None
        if res:
            return jsonify(res)
        else:
            # alert not exists
            abort(404, message='alert not exists')

    def delete(self, alert_id):
        res = self.document.delete_one({'_id': ObjectId(alert_id)})
        if res.raw_result['n'] > 0:
            res = {'msg': 'alerter delete succeed'}
        else:
            res = {'msg': 'alerter delete failed'}
        return res

    def options(self, alert_id):
        res = {'ok': True}
        return res

    def put(self, alert_id):
        args = self.put_parser.parse_args()
        args.to_persons = request.json['to_persons']
        try:
            res = self.document.find_one_and_update(
                {
                    '_id': ObjectId(alert_id),
                },
                {
                    '$set': {
                        'name': args.name,
                        'type': args.type,
                        'to_persons': args.to_persons,
                        'update_time': int(datetime.now().timestamp())
                    }
                })
            if not isinstance(res, dict):
                abort(404, message='alert not exists')
            res.pop('_id')
            return res
        except InvalidId:
            abort(400, message='no allowed id')
