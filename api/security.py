"""
    this module just for token auth
"""
from bson.objectid import ObjectId
from flask import make_response, jsonify, current_app, g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          SignatureExpired,
                          BadSignature)

from . import app

serializer = Serializer(app.config['SECRET_KEY'], expires_in=600)

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='token')
auth = MultiAuth(basic_auth, token_auth)


@token_auth.verify_token
def verify_auth_token(token):
    g.user = None
    try:
        data = serializer.loads(token)
        with app.app_context():
            user = current_app.mongo_conn.document_new('monitor_user').find_one({
                '_id': ObjectId(data['id']),
            })
        g.user = user
        return user

    except (SignatureExpired, BadSignature):
        return False  # valid token, but expired and invalid token


@basic_auth.verify_password
def verify_password(username_or_token, password):
    '''
        token means in auth username
    :param username_or_token:
    :param password:
    :return:
    '''
    # try to authenticate with username/password
    g.user = None
    with app.app_context():
        user = current_app.mongo_conn.document_new('monitor_user').find_one({
            'login_name': username_or_token
        })
    if not user or user['password'] != password:
        return False
    else:
        g.user = user
        return True


@token_auth.error_handler
@basic_auth.error_handler
def unauthorized():
    response = make_response(jsonify({'error': 'Unauthorized access'}), 401)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
