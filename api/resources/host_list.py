from flask_restful import Resource
from api.common.mongo_clt import create_conn


class HostList(Resource):
    """ read only """

    def __init__(self, *args, **kwargs):
        super(HostList, self).__init__(*args, **kwargs)
        self.conn = create_conn()

    def get(self):
        res = self.conn.distinct('tags.hostname')
        return res


class IpList(Resource):
    """ read only """

    def __init__(self, *args, **kwargs):
        super(IpList, self).__init__(*args, **kwargs)
        self.conn = create_conn()

    def get(self):
        tags_lst = self.conn.distinct('tags.host_ip')
        return tags_lst
