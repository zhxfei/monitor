import psutil


def get_cpu_stat():
    # sum(cpu time)/ core per
    cpu_info = psutil.cpu_times_percent(0)
    cpu_per_stat = {
        'cpu.user.percent': cpu_info.user,
        'cpu.system.percent': cpu_info.system,
        'cpu.idle.percent': cpu_info.idle,
        'cpu.iowait.percent': cpu_info.iowait,
        'cpu.irq.percent': cpu_info.irq,
        'cpu.nice.percent': cpu_info.nice,
        'cpu.steal.percent': cpu_info.steal,
    }
    return cpu_per_stat
