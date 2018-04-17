"""
    this module provide some system metric status collect by psutil
"""

import os
import time

import psutil


def get_system_stat(cpu_number=psutil.cpu_count()):
    """ get system status
        only implemented load 1min/5min/15min and 1 min/per core currently
    """

    up_time = int(time.time() - psutil.boot_time())
    system_info = {
        'system.uptime': up_time,
        'system.load.1min': os.getloadavg()[0],
        'system.load.avg.5min': os.getloadavg()[1],
        'system.load.avg.15min': os.getloadavg()[2],
        'system.load.avg.1min/core': os.getloadavg()[0] / cpu_number
    }

    return system_info


def get_disks_info(all_partitions=False):
    """get disk stats"""
    disks_info = {}
    for info in psutil.disk_partitions(all_partitions):
        usage = psutil.disk_usage(info.mountpoint)
        disk_info = {
            # 'df.bytes.total': usage.total,
            # 'df.bytes.used': usage.used,
            'df.bytes.used.percent.%s' % info.mountpoint: usage.percent,
            # 'df.bytes.free': usage.free,
        }

        disks_info.update(disk_info)
    return disks_info


def get_cpu_stat():
    """ get cpu status
        -------
        :return dict
            cpu status info:
                cpu.user.percent: The percentage of user processes in cpu time slices
                cpu.system.percent: The percentage of system processes in cpu time slices
                cpu.idle.percent: The percentage of cpu idle time in cpu time slices
                cpu.iowait.percent: The percentage of wait io in cpu time slices
                cpu.irq.percent: The percentage of IRQ in cpu time slices
                cpu.user.percent: The percentage of niced processes in cpu time slices
                cpu.steal.percent: The percentage of virtual cpu steal time in cpu time slices
        -------
    """
    # sum(cpu time)/ core per
    cpu_info = psutil.cpu_times_percent(0)

    cpu_per_stat = {
        'cpu.user.percent': cpu_info.user,
        'cpu.system.percent': cpu_info.system,
        'cpu.idle.percent': cpu_info.idle,
        'cpu.iowait.percent': cpu_info.iowait,
        'cpu.irq.percent': cpu_info.irq,
        # 'cpu.steal.percent': cpu_info.steal,
        'cpu.nice.percent': cpu_info.nice
    }

    return cpu_per_stat


def get_connections_by_status():
    """get connection status"""
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


def get_memory_stat():
    """ get memory stat"""
    virtual_memory = psutil.virtual_memory()
    swap_memory = psutil.swap_memory()

    memory_info = {
        'mem.virtual.total': virtual_memory.total,
        'mem.virtual.used': virtual_memory.used,
        'mem.virtual.available': virtual_memory.available,
        'mem.virtual.used.percent': virtual_memory.percent,
        'mem.virtual.shared': virtual_memory.shared,
        'mem.virtual.buffers': virtual_memory.buffers,
        'mem.virtual.cached': virtual_memory.cached,
        'mem.virtual.free': virtual_memory.free,
        'mem.virtual.active': virtual_memory.active,
        'mem.virtual.inactive': virtual_memory.inactive,

        # swap memory info
        'mem.swap.total': swap_memory.total,
        'mem.swap.free': swap_memory.free,
        'mem.swap.used': swap_memory.used,
        'mem.swap.percent': swap_memory.percent,
        'mem.swap.in': swap_memory.sin,
        'mem.swap.out': swap_memory.sout
    }
    return memory_info


ps_utils_collect_funcs = {
    'mem_collector': get_memory_stat,
    'system_collector': get_system_stat,
    'cpu_collector': get_cpu_stat,
    'net_dev_collector': get_net_dev_stat,
    'disk_stat_collector': get_disks_info,
    'get_connections_by_status': get_connections_by_status,
}
