from .cpu_status import get_cpu_stat
from .conn_status import get_connections_by_status
from .mem_status import get_memory_stat
from .system_status import get_system_stat
from .net_dev import get_net_dev_stat
from .file_system import get_disks_info


data_collect_funcs = {
    'mem_collector': get_memory_stat,
    'system_collector': get_system_stat,
    'cpu_collector': get_cpu_stat,
    'net_dev_collector': get_net_dev_stat,
    'disk_stat_collector': get_disks_info,
    'get_connections_by_status': get_connections_by_status,
}