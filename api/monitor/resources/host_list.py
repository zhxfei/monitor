from flask_restful import Resource
from flask import current_app

from api import app
from api.security import auth


class HostList(Resource):
    """ read only """
    method_decorators = [auth.login_required]

    def __init__(self):
        with app.app_context():
            self.document = current_app.mongo_conn.document

    def options(self):
        return {'code': 1}

    def get(self):
        res = self.document.distinct('tags.hostname')
        if len(res) is 0:
            print('debug')
        return res


class IpList(Resource):
    """ read only """
    method_decorators = [auth.login_required]

    def __init__(self):
        with app.app_context():
            self.document = current_app.mongo_conn.document

    def options(self):
        return {'code': 1}

    def get(self):
        tags_lst = self.document.distinct('tags.host_ip')
        return tags_lst
