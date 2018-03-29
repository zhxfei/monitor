from flask_restful import Resource, reqparse
from api.common.mongo_clt import create_conn


class MetricList(Resource):
    def __init__(self, *args, **kwargs):
        super(MetricList, self).__init__(*args, **kwargs)
        self.conn = create_conn()
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument(
            'endpoint',
            dest='host',
            type=str,
            location=['json', 'args', 'form'],
            required=True,
            help='The item\'s hostname',
        )

    def get(self):
        """ get metric list by hostname """
        args = self.get_parser.parse_args()
        res = self.conn.distinct('metric', {
            "tags.hostname": args.host
        })
        return res
