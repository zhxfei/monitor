import psutil


def get_disks_info(all_partitions=False):
    # get disk stats
    disks_info = []
    for dp in psutil.disk_partitions(all_partitions):
        usage = psutil.disk_usage(dp.mountpoint)
        disk_info = {
            # 'df.bytes.total': usage.total,
            # 'df.bytes.used': usage.used,
            'df.bytes.used.percent.' + dp.mountpoint: usage.percent,
            # 'df.bytes.free': usage.free,
            'tag': {
                'device': dp.device,
                'type': dp.fstype
            }
        }

        disks_info.append(disk_info)
    return disks_info
