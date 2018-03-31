import psutil


def get_net_dev_stat():
    """get network device stats"""
    net_dev_stats = {}
    net_dev_stat_raw = psutil.net_io_counters(pernic=True)
    for dev_name in net_dev_stat_raw:
        c = net_dev_stat_raw.get(dev_name)
        if not c:
            continue
        net_dev_stat = {
            'net.dev.bytes.sent.%s' % dev_name: c[0],
            'net.dev.bytes.receive.%s' % dev_name: c[1],
            'net.dev.packets.sent.%s' % dev_name: c[2],
            'net.dev.packets.receive.%s' % dev_name: c[3],
            'net.dev.errors.in.%s' % dev_name: c[4],
            'net.dev.errors.out.%s' % dev_name: c[5],
            'net.dev.dropped.in.%s' % dev_name: c[6],
            'net.dev.dropped.out.%s' % dev_name: c[7],

            # to do : add net dev send / receive bytes rate
            # 'send_rate': c['tx_per_sec'],
            # 'recv_rate': c['rx_per_sec']
        }
        net_dev_stats.update(net_dev_stat)
    return net_dev_stats
