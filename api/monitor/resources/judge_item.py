from flask_restful import Resource
from bson.objectid import ObjectId
from flask import current_app

from api import app
from api.security import auth


class JudgeItemList(Resource):
    """ read only """
    method_decorators = [auth.login_required]

    def __init__(self):
        with app.app_context():
            self.policy_document = current_app.mongo_conn.document_new('monitor_policy')
            self.strategy_document = current_app.mongo_conn.document_new('monitor_strategy')

    def get(self):
        response_data = []
        policies = list(self.policy_document.find({}, {'creator': 0, 'owner': 0, 'update_time': 0}))
        for policy in policies:
            for strategy_id in policy.get('strategy_id_lst'):
                strategy = self.strategy_document.find_one({'_id': ObjectId(strategy_id)})
                if strategy:
                    judge_item = dict()
                    judge_item['condition'] = strategy.get('condition')
                    judge_item['metrics'] = strategy.get('metrics')
                    judge_item['tags'] = policy.get('tags')
                    judge_item['monitor_id'] = str(policy.get('_id'))
                    judge_item['update_time'] = strategy.get('update_time')

                    response_data.append(judge_item)
        return response_data
