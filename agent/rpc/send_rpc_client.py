import json
import zerorpc
import logging


class RpcClient:
    def __init__(self, server_host, timeout=30, heart_beat_itv=10):
        self.rpc_server = "tcp://" + server_host
        self.rpc_client = zerorpc.Client(timeout=timeout, heartbeat=heart_beat_itv)
        self.rpc_client.connect(self.rpc_server)

        # record stat
        self.stats_count = None

    def send_mon_data(self, data):
        j_data = self._send_data_encode(data) if isinstance(data, list) else data
        try:
            res = self.rpc_client.upload_data(j_data, async=False)
        except zerorpc.exceptions.LostRemote as e:
            logging.error(e)
            return
        return self._rec_data_decode(res)

    @staticmethod
    def _rec_data_decode(data):
        return json.loads(data)

    @staticmethod
    def _send_data_encode(data):
        return json.dumps(data)
