import json


class Sender:
    @staticmethod
    def rec_data_decode(data):
        """ decode receive data, json loads"""
        return json.loads(data)

    @staticmethod
    def send_data_encode(data):
        """ encode send data, json dumps"""
        return json.dumps(data)

    def data_consume(self, queue):
        """constructor for data consume called in agent main process """
        raise NotImplementedError

    def data_send(self, data):
        """constructor for data send"""
        raise NotImplementedError
