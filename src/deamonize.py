#!/usr/bin/python3 -Es

import argparse
import logging

import gc
import os
import signal

from daemons.prefab import run

import cli
from common import bootstrap
from common.utils import CLI

CMD_START = 'start'
CMD_STOP = 'stop'
CMD_RESTART = 'restart'
ALLOWED_COMMANDS = (CMD_START, CMD_STOP, CMD_RESTART)

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("-c", "--config", dest='config', type=argparse.FileType('r'), required=False,
                    help="File containing JointBox configuration in yaml or JSON format")
parser.add_argument("action", choices=ALLOWED_COMMANDS)


class JointBoxDaemon(run.RunDaemon):
    def __init__(self, logger: logging.Logger, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = None
        self.application = None
        self.logger = logger
        for s in self.kill_signals:
            self.handle(s, self.on_shutdown)

    def on_shutdown(self, *args, **kwargs):
        try:
            self.application.shutdown()
            self.logger.info('Bye')
        except Exception as e:
            self.logger.exception("Unable to shutdown application gracefully")

    def run(self):
        application = bootstrap.bootstrap(self.config)
        self.application = application
        self.logger.info("Started main application loop")
        application.main_loop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        args = parser.parse_args()
        daemon = JointBoxDaemon(logging.getLogger('App'), pidfile=os.path.join(os.getcwd(), "daemon.pid"))
        if args.action == CMD_START:
            if args.config is None:
                config_path = cli.get_default_config_path()
            else:
                config_path = args.config.name
                args.config.close()
            if config_path:
                config = bootstrap.read_config(config_path)
            else:
                raise Exception("Please specify config file")
            gc.collect()
            daemon.config = config
            daemon.start()
        elif args.action == CMD_STOP:
            daemon.stop()
        elif args.action == CMD_RESTART:
            daemon.restart()
    except Exception as e:
        CLI.print_error(e)
