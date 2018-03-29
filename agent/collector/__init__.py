"""
def get_expensive_proc():
    process_list = []
    max_cpu_percent = 0.0
    max_mem_percent = 0.0
    max_cpu_info = None
    max_mem_info = None
    for p in psutil.process_iter():
        # psutil throws a KeyError when the uid of a process is not associated with an user.
        try:
            username = p.username()
        except KeyError:
            username = None
        p_mem = p.memory_percent()
        p_cpu = p.cpu_percent(0)
        if p_mem <= max_mem_percent and p_cpu <= max_cpu_percent:
            continue
        if p_mem > max_mem_percent:
            max_mem_info = {
                'max_mem_proc_percent': p.memory_percent(),
                'tag': ' '.join(
                    [
                        'name: ' + p.name(),
                        'cmdline: ' + ' '.join(p.cmdline())[:100],
                        'user: ' + username
                    ]
                )
            }
            max_mem_percent = p_mem
        if p_cpu > max_cpu_percent:
            max_cpu_info = {
                'max_cpu_proc_percent': p.cpu_percent(0),
                'tag': ' '.join(
                    [
                        'name: ' + p.name(),
                        'cmdline: ' + ' '.join(p.cmdline())[:100],
                        'user: ' + username
                    ]
                )
            }
            max_cpu_percent = p_cpu
    process_list.append(max_cpu_info)
    process_list.append(max_mem_info)
    return process_list

def get_cpu_cores():
    return [c._asdict() for c in psutil.cpu_times_percent(0, percpu=True)]

def get_disks_counters(perdisk=True):
    return dict((dev, c._asdict()) for dev, c in psutil.disk_io_counters(perdisk=perdisk).items())

"""
