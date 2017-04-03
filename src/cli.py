import argparse
import os

from common import bootstrap

# Locations to be tried for guessing config file if none specified
from common.utils import CLI

DEFAULT_CONFIG_LOCATIONS = [
    './config.yaml',
    './config.yml',
]

supplementary_parser = argparse.ArgumentParser(add_help=False)
supplementary_parser.add_argument("-c", "--config", dest='config', type=argparse.FileType('r'), required=False,
                                  help="File containing JointBox configuration in yaml or JSON format")

parser = argparse.ArgumentParser(prog='jointbox',
                                 description='Your DIY Smart home. Made easy.',
                                 formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument("-c", "--config", dest='config', type=argparse.FileType('r'), required=False,
                    help="File containing JointBox configuration in yaml or JSON format")

parser.add_argument("-V", "--verbose", dest="verbose", action='store_true', required=False,
                    help="If set more verbose output will used",
                    default=False)

module_parser = parser.add_subparsers(title="module",
                                      dest="module",
                                      description='Use \"<MODULE_NAME> -h\" to get information '
                                                  'about command available for particular module')

namespace_parsers = {}


def get_default_config_path():
    for config_path in DEFAULT_CONFIG_LOCATIONS:
        if os.path.isfile(config_path):
            return config_path
    return None


if __name__ == '__main__':
    known, unknown = supplementary_parser.parse_known_args()
    if known.config is None:
        config_path = get_default_config_path()
    else:
        config_path = known.config.name
        known.config.close()
    if config_path:
        CLI.print_info("Loaded config: " + os.path.realpath(config_path))
        CLI.print_info("")
        config = bootstrap.read_config(config_path)
    else:
        config = {}
    application = bootstrap.bootstrap_cli(config)
    # process CLI extensions
    for namespace, ext in application.cli_extensions:
        if namespace not in namespace_parsers.keys():
            p = module_parser.add_parser(namespace)
            namespace_parsers[namespace] = p.add_subparsers(title='module_cmd', dest='module_cmd')
        ext_parser = namespace_parsers[namespace]
        ext_subparser = ext_parser.add_parser(ext.COMMAND_NAME,
                                              help=ext.COMMAND_DESCRIPTION)
        ext.setup_parser(ext_subparser)
        ext_instance = ext(ext_subparser, application)
        ext_subparser.set_defaults(handler=ext_instance)

    args = parser.parse_args()
    if hasattr(args, "handler"):
        args.handler.handle(args)
