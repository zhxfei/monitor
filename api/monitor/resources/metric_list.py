from flask_restful import Resource, reqparse
from flask import current_app

from api import app
from api.security import auth


class MetricList(Resource):
    method_decorators = [auth.login_required]

    def __init__(self):
        with app.app_context():
            self.document = current_app.mongo_conn.document

        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument(
            'endpoint',
            dest='host',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='The item\'s hostname',
        )

    def options(self):
        return {'code': 1}

    def get(self):
        """ get metric list by hostname """
        args = self.get_parser.parse_args()
        res = self.document.distinct('metric', {
            "tags.hostname": args.host
        })
        return res
