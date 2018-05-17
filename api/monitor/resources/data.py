from flask_restful import Resource, reqparse
from flask import current_app, abort
from pymongo import ASCENDING, DESCENDING

from api import app
from api.security import auth


class MonitorData(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        with app.app_context():
            self.document = current_app.mongo_conn.document

        self.post_parser = reqparse.RequestParser()
        self.post_parser.add_argument(
            'endpoint',
            dest='host',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='The item\'s hostname',
        )

        self.post_parser.add_argument(
            'metric',
            dest='item',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='The item\'s name',
        )

        self.post_parser.add_argument(
            's_time',
            dest='s_time',
            type=float,
            location=['json', 'args', 'form'],
            required=True,
            help='The item\'s start time',
        )

        self.post_parser.add_argument(
            'e_time',
            dest='e_time',
            type=float,
            location=['json', 'args', 'form'],
            required=True,
            help='The item\'s end time',
        )

        self.post_parser.add_argument(
            'limit',
            dest='limit',
            type=int,
            location=['json', 'args', 'form'],
            required=False,
            help='The item\'s search limit',
        )

    def options(self):
        res = {'ok': True}
        return res

    def post(self):
        args = self.post_parser.parse_args()
        # todo: tags and counterType should be only an external mark
        if not args.limit:
            # asc return limit num items
            return list(self.document.find({
                "tags.hostname": args.host,
                "metric": args.item,
                "timestamp": {
                    '$gte': args.s_time,
                    '$lte': args.e_time
                }
            }, {
                'value': 1,
                '_id': 0,
                'timestamp': 1,
                'step': 1,
                'tags': 1,
                'counterType': 1
            }).sort('timestamp', ASCENDING).limit(60 * 24 * 7))
        else:
            # desc return limit num items
            return list(self.document.find({
                "tags.hostname": args.host,
                "metric": args.item,
                "timestamp": {
                    '$gte': args.s_time,
                    '$lte': args.e_time
                }
            }, {
                'value': 1,
                '_id': 0,
                'timestamp': 1,
                'step': 1,
                'tags': 1,
                'counterType': 1
            }).sort('timestamp', DESCENDING).limit(args.limit))

    def delete(self):
        args = self.post_parser.parse_args()
        res = self.document.delete_many({
            "tags.hostname": args.host,
            "timestamp": {
                '$lte': args.s_time
            }
        })
        if res:
            return res.raw_result
        else:
            abort(405)
