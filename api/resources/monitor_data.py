from flask_restful import Resource, reqparse
from flask import jsonify
from api.common.mongo_clt import create_conn


class MonitorData(Resource):
    def __init__(self):
        self.conn = create_conn()
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
        res = jsonify({'ok': True})
        res.headers['Access-Control-Allow-Origin'] = '*'
        res.headers['Access-Control-Allow-Methods'] = 'DELETE'
        res.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
        return res

    def post(self):
        args = self.post_parser.parse_args()
        if not args.limit:
            # asc return limit num items
            return list(self.conn.find({
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
                }
            ).sort('timestamp', 1).limit(100000))
        else:
            # desc return limit num items
            return list(self.conn.find({
                "tags.hostname": args.host,
                "metric": args.item,
                "timestamp": {
                    '$lte': args.e_time
                }
            }, {
                'value': 1,
                '_id': 0,
                'timestamp': 1,
                'step': 1,
                'tags': 1,
                'counterType': 1
            }).sort('timestamp', -1).limit(args.limit))

    def delete(self):
        args = self.post_parser.parse_args()
        res = self.conn.delete_many({
            "tags.hostname": args.host,
            "timestamp": {
                '$lte': args.s_time
            }
        })
        return jsonify(res.raw_result)
