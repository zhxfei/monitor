if __name__ == '__main__':
    from gevent import monkey

    monkey.patch_all()

    import argparse

    from api import app
    from gevent.pywsgi import WSGIServer

    description = '''EaseMonitor Restful API design for data search'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-a', '--host',
                        required=True,
                        dest='host',
                        type=str,
                        action='store',
                        help='define Monitor API server host listening')

    parser.add_argument('-p', '--port',
                        required=True,
                        dest='port',
                        type=int,
                        action='store',
                        help='define Monitor API server host listening')

    args = parser.parse_args()
    server = WSGIServer((args.host, args.port), app)

    # server = WSGIServer(('0.0.0.0', 11111), app)
    server.serve_forever()
    # app.run('0.0.0.0', 11111)
