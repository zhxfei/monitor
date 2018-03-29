import psutil


def get_connections_by_status():
    connections = {
        'net.conn.syn_recv': 0,
        'net.conn.time_wait': 0,
        'net.conn.listen': 0,
        'net.conn.established': 0
    }

    for tcp_conn in psutil.net_connections(kind='tcp4'):
        if not tcp_conn.status:
            continue
        elif tcp_conn.status == 'LISTEN':
            connections['net.conn.listen'] += 1
        elif tcp_conn.status == 'SYN_RECV':
            connections['net.conn.syn_recv'] += 1
        elif tcp_conn.status == 'TIME_WAIT':
            connections['net.conn.time_wait'] += 1
        elif tcp_conn.status == 'ESTABLISHED':
            connections['net.conn.established'] += 1
        else:
            continue

    return connections
