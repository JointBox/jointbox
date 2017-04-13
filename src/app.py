#!/usr/bin/env python -Es

import gc
import logging
import cli
from common.bootstrap import bootstrap
from common.core import ApplicationManager
from common.utils import CLI

logger = logging.getLogger('App')


def run_application(config: dict, application: ApplicationManager = None):
    if application is None:
        # Do bootstrap
        application = bootstrap(config)
    try:
        logger.info("Started main application loop")
        application.main_loop()
    except KeyboardInterrupt:
        application.shutdown()
        logger.info("Bye")
        exit()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    try:
        config = cli.read_config_from_arguments()
        gc.collect()
    except Exception as e:
        CLI.print_error(e)
    run_application(config)
