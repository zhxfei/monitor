"""
    this module is flask route for user login and get a token
"""
from flask import request, jsonify, g

from . import app
from .security import auth, serializer


@app.route('/monitor/v1/token', methods=['OPTIONS', 'GET', 'HEAD'])
@auth.login_required
def get_auth_token():
    if request.method == 'GET':
        token_id = str(g.user['_id'])
        token = serializer.dumps({'id': token_id})
        res = jsonify({'token': token.decode('ascii'), 'duration': 600})
    else:
        res = jsonify({'code': 1})
    res.headers.extend({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,OPTION,DELETE',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization'
    })
    return res


@app.route('/monitor/v1/current_user', methods=['OPTIONS', 'GET', 'HEAD'])
@auth.login_required
def current_user():
    if request.method == 'GET':
        for item in ['_id', 'password']:
            g.user.pop(item)
        res = jsonify(g.user)
    else:
        res = jsonify({'code': 1})
    res.headers.extend({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,OPTION,DELETE',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization'
    })
    return res
