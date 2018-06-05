if __name__ == '__main__':
    from gevent import monkey

    monkey.patch_all()

    import logging

    import gevent

    logging.basicConfig(
        # filename=self.config.var_dict.get('logfile') or None,
        level=logging.DEBUG,
        format="[%(asctime)s] >>> %(levelname)s  %(name)s: %(message)s"
    )
    logging.info('watcher log init succeed...')

    from watcher.judger import Judge

    job_lst = []
    j = Judge()

    job_lst.append(gevent.spawn(j.sync_judge_item))
    job_lst.append(gevent.spawn_later(0.5, j.pull_monitor_item))
    job_lst.append(gevent.spawn_later(0.5, j.judge_loop))

    gevent.joinall(job_lst)
