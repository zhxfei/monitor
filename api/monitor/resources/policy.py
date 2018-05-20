from datetime import datetime

from flask_restful import Resource, reqparse, abort
from flask import jsonify, current_app, g, request
from bson.objectid import ObjectId
from bson.errors import InvalidId

from api import app
from api.security import auth


class PolicyList(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        with app.app_context():
            self.strategy_document = current_app.mongo_conn.document_new('monitor_strategy')
            self.alerter_document = current_app.mongo_conn.document_new('monitor_alert')
            self.document = current_app.mongo_conn.document_new('monitor_policy')

        self.post_parser = reqparse.RequestParser()

        self.post_parser.add_argument(
            'name',
            dest='name',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='monitor name not null',
        )
        self.post_parser.add_argument(
            'strategy_id_lst',
            dest='strategy_id_lst',
            type=list,
            location=['json', 'args', 'form'],
            required=True,
            help='strategy_id_lst should be a list',
        )
        self.post_parser.add_argument(
            'alerter_id_lst',
            dest='alerter_id_lst',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='alerter_id_lst should be a list',
        )
        self.post_parser.add_argument(
            'tags',
            dest='tags',
            type=dict,
            location=['json', 'args', 'form'],
            required=True,
            help=' monitor tags should be a dict',
        )

    def get(self):
        res = []
        login_user = g.user['login_name']
        strategy_lst = self.document.find({})
        for strategy in strategy_lst:
            if login_user in strategy['owner']:
                strategy_id = str(strategy.pop('_id'))
                strategy['monitor_id'] = strategy_id
                res.append(strategy)
        return res

    def options(self):
        return {'code': 1}

    def post(self):
        try:
            args = self.post_parser.parse_args()
            res = self.document.find_one({
                'name': args.name
            })

            # reqparser could't parse list
            args.strategy_id_lst = request.json['strategy_id_lst']
            args.alerter_id_lst = request.json['alerter_id_lst']

            if res is None:
                if self.exists_check(args.strategy_id_lst, self.strategy_document) \
                        and self.exists_check(args.alerter_id_lst, self.alerter_document):
                    # add new policy
                    res = self.document.insert_one({
                        'name': args.name,
                        'strategy_id_lst': args.strategy_id_lst,
                        'alerter_id_lst': args.alerter_id_lst,
                        'tags': args.tags,
                        'owner': [g.user['login_name'], ],  # owner is a user list
                        'creator': g.user['login_name'],
                        'update_time': int(datetime.now().timestamp())
                    })

                    # add new judge items
                    return {'_id': str(res.inserted_id)}
                else:
                    abort(400, message='strategy id or alert id is not exists')
            else:
                abort(400, message="monitor name {} has exist".format(args.name))
        except InvalidId:
            abort(400, message="invalid object id")

    @staticmethod
    def exists_check(check_id_lst, document):
        for check_id in check_id_lst:
            if check_id:
                res = document.find_one({
                    '_id': ObjectId(check_id)
                }, {'_id': 0})
                if res is None:
                    return False
        return True


class Policy(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        with app.app_context():
            self.document = current_app.mongo_conn.document_new('monitor_policy')

        self.put_parser = reqparse.RequestParser()
        self.put_parser.add_argument(
            'name',
            dest='name',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='monitor name not null',
        )
        self.put_parser.add_argument(
            'strategy_id_lst',
            dest='strategy_id_lst',
            type=list,
            location=['json', 'args', 'form'],
            required=True,
            help='strategy_id_lst should be a list',
        )
        self.put_parser.add_argument(
            'alerter_id_lst',
            dest='alerter_id_lst',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='alerter_id_lst should be a list',
        )
        self.put_parser.add_argument(
            'tags',
            dest='tags',
            type=dict,
            location=['json', 'args', 'form'],
            required=True,
            help=' monitor tags should be a dict',
        )

    def get(self, monitor_id):
        try:
            if monitor_id:
                res = self.document.find_one({
                    '_id': ObjectId(monitor_id)
                }, {'_id': 0})
            else:
                res = None
            if res:
                return jsonify(res)
            else:
                abort(404, message='monitor not exists')
        except InvalidId:
            abort(400, message='no allowed monitor id')

    def delete(self, monitor_id):
        try:
            res = self.document.delete_one({'_id': ObjectId(monitor_id)})
            if res.raw_result['n'] > 0:
                res = {'msg': 'monitor delete succeed'}
            else:
                abort(400, message='monitor delete failed, monitor may not exists')
            return res
        except InvalidId:
            abort(400, message='no allowed monitor id')

    def options(self, monitor_id):
        res = {'ok': True}
        return res

    def put(self, monitor_id):
        args = self.put_parser.parse_args()
        args.strategy_id_lst = request.json['strategy_id_lst']
        args.alerter_id_lst = request.json['alerter_id_lst']
        try:
            res = self.document.find_one_and_update(
                {
                    '_id': ObjectId(monitor_id),
                },
                {
                    '$set': {
                        'name': args.name,
                        'strategy_id_lst': args.strategy_id_lst,
                        'alerter_id_lst': args.alerter_id_lst,
                        'tags': args.tags,
                        'update_time': int(datetime.now().timestamp())
                    }
                })
            if not isinstance(res, dict):
                abort(404, message='monitor not exists')
            res.pop('_id')
            return res
        except InvalidId:
            abort(400, message='no allowed monitor id')
