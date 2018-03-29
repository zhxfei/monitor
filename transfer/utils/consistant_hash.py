import zlib
from collections import OrderedDict
from hashlib import md5


class ConsistentHashRing:
    def __init__(self, nodelist=None, v_nodes=10000):
        self.nodelist = [k + ':' + v for k, v in nodelist.items()]
        self.v_nodes = v_nodes
        self.ring = OrderedDict()
        for node in self.nodelist:
            self.add_node(node)
        self._sort_v_node_list = sorted([v_node for inner in self.ring.values()
                                         for v_node in inner])

    def add_node(self, node):
        v_node_list = [self.gen_key(node + ":" + str(v_node))
                       for v_node in range(self.v_nodes)]
        self.ring.update({
            node: v_node_list
        })

    def remove_node(self, node):
        self.nodelist.remove(node)
        self.ring.pop(node)
        self._sort_v_node_list = sorted([v_node for inner in self.ring.values()
                                         for v_node in inner])

    @staticmethod
    def gen_key(node):
        # return int(md5(node.encode('utf-8')).hexdigest(), base=16)
        return zlib.crc32(node.encode('utf-8'))

    def get_node(self, key):
        crc_v = self.gen_key(key)
        big_node_lst = [v_node for v_node in self._sort_v_node_list
                        if v_node > crc_v]
        if big_node_lst:
            return self.get_real_node(big_node_lst[0])
        return self.get_real_node(self._sort_v_node_list[0])

    def get_real_node(self, v_node):
        for k, v in self.ring.items():
            if v_node in v:
                return k.split(':')[0]

    def show_server(self):
        print('-' * 5 + 'the consistance hash ring contain server' + '-' * 5)
        print(self.ring.keys())

"""
# consistent hash test:
# -----------
def get_links_by_html(html):
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)

server_list = ['127.0.0.1:6070',
               '127.0.0.1:6071',
               '127.0.0.1:6072']


ring = ConsistentHashRing(server_list)

print(ring.get_node('HP-ENVYmem.swap.used'))
print(ring.get_node('HP-ENVYmem.virtual.available'))
print(ring.get_node('HP-ENVYmem.virtual.used'))


t1 = time.time()

ring.show_server()
test_server_list = map(ring.get_node, set(get_links_by_html(
    requests.get('http://zhxfei.com/').text)))
print(Counter(list(test_server_list)))

print('COST: {}'.format(time.time() - t1))
# ------
# (env) zhxfei@HP-ENVY:~/PycharmProjects/EasyMonitorTransfer/consistent_hash$ python __init__.py
# 127.0.0.1:6071
# 127.0.0.1:6070
# 127.0.0.1:6071
# -----the consistance hash ring contain server-----
# odict_keys(['127.0.0.1:6070', '127.0.0.1:6071', '127.0.0.1:6072'])
# Counter({'127.0.0.1:6071': 18, '127.0.0.1:6072': 17, '127.0.0.1:6070': 16})
# COST: 0.3761754035949707

"""
