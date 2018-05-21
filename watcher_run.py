
if __name__ == '__main__':
    import gevent

    from gevent import monkey
    monkey.patch_all()

    import logging
    logging.basicConfig()

    from watcher.judger import Judge
    job_lst = []
    j = Judge()
    job_lst.append(gevent.spawn(j.pull_monitor_item))
    job_lst.append(gevent.spawn(j.sync_judge_item))
    job_lst.append(gevent.spawn(j.judge_loop))

    gevent.joinall(job_lst)