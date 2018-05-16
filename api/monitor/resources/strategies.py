from datetime import datetime

from flask_restful import Resource, reqparse
from flask import jsonify, current_app, g, abort
from bson.objectid import ObjectId
from bson.errors import InvalidId

from api import app
from api.security import auth


class StrategyList(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        with app.app_context():
            self.document = current_app.mongo_conn.document_new('monitor_strategy')

        self.post_parser = reqparse.RequestParser()

        self.post_parser.add_argument(
            'name',
            dest='name',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='strategy name not null',
        )
        self.post_parser.add_argument(
            'condition',
            dest='condition',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='strategy condition not null',
        )
        self.post_parser.add_argument(
            'metrics',
            dest='metrics',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='strategy metrics not null',
        )
        self.post_parser.add_argument(
            'grade',
            dest='grade',
            type=int,
            location=['json', 'args', 'form'],
            required=True,
            help=' strategy grade should be integer',
        )

    def get(self):
        res = []
        login_user = g.user['login_name']
        strategy_lst = self.document.find({})
        for strategy in strategy_lst:
            if login_user in strategy['owner']:
                strategy_id = str(strategy.pop('_id'))
                strategy['strategy_id'] = strategy_id
                res.append(strategy)
        return res

    def options(self):
        return {'code': 1}

    def post(self):
        args = self.post_parser.parse_args()
        res = self.document.find_one({
            'name': args.name
        })
        if res is None:
            res = self.document.insert_one({
                'name': args.name,
                'metrics': args.metrics,
                'grade': args.grade,
                'condition': args.condition,
                'owner': [g.user['login_name'], ],  # owner is a user list
                'creator': g.user['login_name'],
                'update_time': int(datetime.now().timestamp())
            })
            return {'_id': str(res.inserted_id)}
        else:
            # user exists
            abort(400, message="strategy name {} has exist".format(args.name))


class Strategy(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        with app.app_context():
            self.document = current_app.mongo_conn.document_new('monitor_strategy')

        self.put_parser = reqparse.RequestParser()
        self.put_parser.add_argument(
            'name',
            dest='name',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='strategy name not null',
        )
        self.put_parser.add_argument(
            'condition',
            dest='condition',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='strategy condition not null',
        )
        self.put_parser.add_argument(
            'metrics',
            dest='metrics',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='strategy metrics not null',
        )
        self.put_parser.add_argument(
            'grade',
            dest='grade',
            type=int,
            location=['json', 'args', 'form'],
            required=True,
            help=' strategy grade not null',
        )

    def get(self, strategy_id):
        try:
            if strategy_id:
                res = self.document.find_one({
                    '_id': ObjectId(strategy_id)
                }, {'_id': 0})
            else:
                res = None
            if res:
                return jsonify(res)
            else:
                abort(404, 'strategy not exists')
        except InvalidId:
            abort(400, 'no allowed strategy id')

    def delete(self, strategy_id):
        try:
            res = self.document.delete_one({'_id': ObjectId(strategy_id)})
            if res.raw_result['n'] > 0:
                res = {'msg': 'Strategy delete succeed'}
            else:
                res = {'msg': 'Strategy delete failed'}
            return res
        except InvalidId:
            abort(400, message='no allowed strategy id')

    def options(self, strategy_id):
        res = {'ok': True}
        return res

    def put(self, strategy_id):
        args = self.put_parser.parse_args()
        try:
            res = self.document.find_one_and_update(
                {
                    '_id': ObjectId(strategy_id),
                },
                {
                    '$set': {
                        'name': args.name,
                        'condition': args.condition,
                        'metrics': args.metrics,
                        'grade': args.grade,
                        'update_time': int(datetime.now().timestamp())
                    }
                })
            if not isinstance(res, dict):
                abort(404, message='strategy not exists')
            res.pop('_id')
            return res
        except InvalidId:
            abort(400, message='no allowed strategy id')
