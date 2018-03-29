import time
import os

import psutil

cpu_core_num = psutil.cpu_count()


def get_system_stat():
    # get system stats
    global cpu_core_num
    up_time = int(time.time() - psutil.boot_time())
    system_info = {
        'system.uptime': up_time,
        'system.load.1min': os.getloadavg()[0],
        'system.load.avg.5min': os.getloadavg()[1],
        'system.load.avg.15min': os.getloadavg()[2],
        'system.load.avg.1min/core': os.getloadavg()[0] / cpu_core_num
    }

    return system_info
