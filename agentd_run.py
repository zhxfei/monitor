import argparse
import logging
import sys

from agent.agentd.agentd import MonitorAgent

if __name__ == '__main__':
    description = '''Monitor agent design for data collect'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-c', '--config',
                        metavar='CONF_FILE_PATH',
                        required=False,
                        default='/home/zhxfei/PycharmProjects/EaseMonitorBak/agent/agent_config.json',
                        dest='config_path',
                        action='store',
                        help='define Monitor Agent configuration file path')
    try:
        args = parser.parse_args()

        agent = MonitorAgent()
        agent.config_init(args.config_path)
        agent.serve_forever()
    except KeyboardInterrupt as e:
        logging.info("!!! Agent exit")
        sys.exit(0)
    except Exception as e:
        logging.critical('!!! unknown problem')
        logging.critical(e)
        sys.exit(4)