from flask import make_response, jsonify

from . import app


@app.errorhandler(404)
def not_found(error):
    resp = make_response(jsonify({'error': str(error)}), 404)
    resp.headers.extend({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,OPTION,DELETE',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization'
    })
    print(resp.headers)
    return resp


@app.errorhandler(400)
def not_found(error):
    resp = make_response(jsonify({'error': str(error)}), 400)
    resp.headers.extend({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,OPTION,DELETE',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization'
    })
    return resp
