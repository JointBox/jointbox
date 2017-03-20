import gc
import logging
import yaml

from common.bootstrap import bootstrap

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('App')
    try:
        config_file_name = './config.yaml'
        with open(config_file_name, 'r') as config_file:
            config = yaml.load(config_file)
        gc.collect()
    except Exception as e:
        logger.error("Unable to read config file")
        raise e
    # Do bootstrap
    application = bootstrap(config)
    try:
        logger.info("Started main application loop")
        application.main_loop()
    except KeyboardInterrupt:
        application.shutdown()
        logger.info("Bye")
        exit()
