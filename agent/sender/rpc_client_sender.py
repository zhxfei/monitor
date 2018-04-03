import logging

from zerorpc.exceptions import (LostRemote, TimeoutExpired, RemoteError)
import gevent

from agent.config.default_config import DEFAULT_SENDER_SLEEP_TIME
from agent.sender.base_sender import Sender
from common.rpc.rpc_client import RPCClient


class AgentRPCClient(RPCClient, Sender):
    """
        Agent RPC client: agent sender with RPCClient
            RPCClient: init a rpc client
            Sender : data send logic
    """

    def data_send(self, data):
        """ send data with rpc client """
        data_encoded = self.send_data_encode(data)
        try:
            res = self.rpc_client.upload_data(data_encoded, async=False)
        except (LostRemote, TimeoutExpired, RemoteError) as error_info:
            logging.error(str(error_info))
        else:
            return self.rec_data_decode(res)

    def data_consume(self, queue):
        """ data consume logic """
        while True:
            while not queue.empty():
                data = queue.get_nowait()
                if data:
                    self._data_push(data)
                else:
                    logging.info('Data Consumer free and will sleeping...')
                    break
            gevent.sleep(DEFAULT_SENDER_SLEEP_TIME)

    def _data_push(self, processed_data):
        """ data push logic """
        response = self.data_send(processed_data)
        if response and response.get('ok'):
            logging.debug('Send monitor data succeed')
        else:
            logging.info('Send monitor data failed')

    @classmethod
    def from_config(cls, config):
        """ get instance from config
        :param config dict
            the dict in agent configuration file about transfer
        """
        return cls(**config)
