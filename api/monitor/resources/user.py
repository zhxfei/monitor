from datetime import datetime

from flask_restful.inputs import boolean
from flask_restful import Resource, reqparse
from flask import jsonify, abort, current_app
from bson.objectid import ObjectId

from api import app
from api.security import auth


class UserList(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        with app.app_context():
            self.document = current_app.mongo_conn.document_new('monitor_user')

        self.post_parser = reqparse.RequestParser()
        self.post_parser.add_argument(
            'username',
            dest='username',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='username not null',
        )
        self.post_parser.add_argument(
            'login_name',
            dest='login_name',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='login name not null and should be unique',
        )
        self.post_parser.add_argument(
            'password',
            dest='password',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='password not null',
        )
        self.post_parser.add_argument(
            'admin',
            dest='is_admin',
            type=boolean,
            location=['json', 'args', 'form'],
            required=False,
            default=False,
            help='user role not null',
        )
        self.post_parser.add_argument(
            'email',
            dest='email',
            type=str,
            location=['json', 'args', 'form'],
            required=False,
            default='',
            help='email of user',
        )
        self.post_parser.add_argument(
            'phone',
            dest='phone',
            type=str,
            location=['json', 'args', 'form'],
            required=False,
            default='',
            help='Phone number of user',
        )
        self.post_parser.add_argument(
            'add_time',
            dest='add_time',
            type=int,
            location=['json', 'args', 'form'],
            required=False,
            default=int(datetime.now().timestamp()),
            help='timestamp',
        )
        self.post_parser.add_argument(
            'comments',
            dest='comments',
            type=str,
            location=['json', 'args', 'form'],
            required=False,
            default='',
            help='Some comments of user',
        )

    def get(self):
        res = []
        user_lst = self.document.find({}, {'password': 0, 'login_name': 0})
        for user in user_lst:
            user_id = str(user.pop('_id'))
            user['user_id'] = user_id
            res.append(user)
        return res

    def options(self):
        return {'code': 1}

    def post(self):
        args = self.post_parser.parse_args()
        res = self.document.find_one({
            'login_name': args.login_name
        })
        if res is None:
            res = self.document.insert_one({
                'username': args.username,
                'login_name': args.login_name,
                'password': args.password,
                'is_admin': args.is_admin,
                'email': args.email,
                'phone': args.phone,
                'add_time': args.add_time,
                'comments': args.comments
            })
            return {'_id': str(res.inserted_id)}
        else:
            # user exists
            abort(400, "login name {} has exist".format(args.login_name))


class User(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        with app.app_context():
            self.document = current_app.mongo_conn.document_new('monitor_user')

        self.put_parser = reqparse.RequestParser()
        self.put_parser.add_argument(
            'username',
            dest='username',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='username not null',
        )
        self.put_parser.add_argument(
            'admin',
            dest='is_admin',
            type=boolean,
            location=['json', 'args', 'form'],
            required=True,
            help='user role not null',
        )
        self.put_parser.add_argument(
            'email',
            dest='email',
            type=str,
            location=['json', 'args', 'form'],
            required=False,
            default='',
            help='email of user',
        )
        self.put_parser.add_argument(
            'phone',
            dest='phone',
            type=str,
            location=['json', 'args', 'form'],
            required=False,
            default='',
            help='Phone number of user',
        )
        self.put_parser.add_argument(
            'add_time',
            dest='add_time',
            type=int,
            location=['json', 'args', 'form'],
            required=False,
            default=int(datetime.now().timestamp()),
            help='timestamp',
        )
        self.put_parser.add_argument(
            'comments',
            dest='comments',
            type=str,
            location=['json', 'args', 'form'],
            required=False,
            default='',
            help='Some comments of user',
        )

    def get(self, user_id):
        if user_id:
            res = self.document.find_one({
                '_id': ObjectId(user_id)
            }, {'_id': 0, 'password': 0, 'login_name': 0})
        else:
            res = None
        if res:
            return jsonify(res)
        else:
            # user not exists
            abort(404)

    def delete(self, user_id):
        res = self.document.delete_one({'_id': ObjectId(user_id)})
        if res.raw_result['n'] > 0:
            res = {'msg': 'User delete succeed'}
        else:
            res = {'msg': 'User delete failed'}
        return res

    def options(self, user_id):
        res = {'ok': True}
        return res

    def put(self, user_id):
        args = self.put_parser.parse_args()
        res = self.document.find_one_and_update(
            {
                '_id': ObjectId(user_id),
            },
            {
                '$set': {
                    'username': args.username,
                    'is_admin': args.is_admin,
                    'email': args.email,
                    'phone': args.phone,
                    'comments': args.comments,
                    'add_time': args.add_time
                }
            })
        if not isinstance(res, dict):
            abort(404)
        res.pop('_id')
        return res