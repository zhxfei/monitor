# import json
# import zerorpc

# class SendRpcClient:
#     """ Reserved for to do test, remove redis, use rpc send data to backend for data store and judge"""
#     def __init__(self, server_host, timeout=30, heart_beat_itv=5):
#         self.rpc_server = "tcp://" + server_host
#         self.rpc_client = zerorpc.Client(timeout=timeout, heartbeat=heart_beat_itv)
#
#         # record stat
#         self.stats_count = None
#
#     def conn_init(self):
#         self.rpc_client.connect(self.rpc_server)
#
#     def send_2_backend(self, data_lst):
#         # notify: redis pop data type is bytes
#         data = json.dumps(data_lst)
#         print('data will send to rpc server')
#         # print(data)
# #        res = self.rpc_client.upload_data(data, async=False)
# #        print(res)
#         return
