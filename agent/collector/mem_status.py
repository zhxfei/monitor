import psutil


def get_memory_stat():
    # get memory stat
    virtual_memory = psutil.virtual_memory()
    sm = psutil.swap_memory()

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
        'mem.swap.total': sm.total,
        'mem.swap.free': sm.free,
        'mem.swap.used': sm.used,
        'mem.swap.percent': sm.percent,
        'mem.swap.in': sm.sin,
        'mem.swap.out': sm.sout
    }
    return memory_info



