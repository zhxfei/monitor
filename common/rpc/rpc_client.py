import logging

import zerorpc


class RPCClient:
    def __init__(self, host=None, port=None, timeout=30, heartbeat=10):
        self.rpc_server = "tcp://%s:%d" % (host, port)
        logging.info("RPC client init...")

        self.rpc_client = zerorpc.Client(timeout=timeout, heartbeat=heartbeat)
        self.rpc_client.connect(self.rpc_server)
        logging.info("RPC client Connect Success")
