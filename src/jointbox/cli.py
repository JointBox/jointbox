#!/usr/bin/env python

#    JointBox - Your DIY smart home. Simplified.
#    Copyright (C) 2017 Dmitry Berezovsky
#    
#    JointBox is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    JointBox is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse

import gc

import logging
import os

from jointbox import app
from jointbox.common import bootstrap

# Locations to be tried for guessing config file if none specified
from jointbox.common.model import CliExtension
from jointbox.common.utils import CLI

DEFAULT_CONFIG_LOCATIONS = [
    './config.yaml',
    './config.yml',
]

supplementary_parser = argparse.ArgumentParser(add_help=False)
supplementary_parser.add_argument("-c", "--config", dest='config', type=argparse.FileType('r'), required=False,
                                  help="File containing JointBox configuration in yaml or JSON format")

parser = argparse.ArgumentParser(prog='jointbox', add_help=True,
                                 description='Your DIY Smart home. Made easy.',
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog="""
--------------------------------------------------------------
JointBox Copyright (C) 2017 Dmitry Berezovsky
This program comes with ABSOLUTELY NO WARRANTY;
This is free software, and you are welcome to redistribute it
under certain conditions;
--------------------------------------------------------------
"""
)

parser.add_argument("-c", "--config", dest='config', type=argparse.FileType('r'), required=False,
                    help="File containing JointBox configuration in yaml or JSON format")

parser.add_argument("-V", "--verbose", dest="verbose", action='store_true', required=False,
                    help="If set more verbose output will used",
                    default=False)

module_parser = parser.add_subparsers(title="module",
                                      dest="module",
                                      description='Use \"<MODULE_NAME> -h\" to get information '
                                                  'about command available for particular module')

_config = None
namespace_parsers = {}


class ServerRunCLIExtension(CliExtension):
    COMMAND_NAME = 'run'
    COMMAND_DESCRIPTION = 'Runs joint-box server in the interactive mode'

    def handle(self, args):
        global _config
        bootstrapped_app = bootstrap.bootstrap_from_cli(_config, self.get_application_manager())
        app.run_application(_config, bootstrapped_app)


class ServerStartDaemonCLIExtension(CliExtension):
    COMMAND_NAME = 'start'
    COMMAND_DESCRIPTION = 'Starts server in the daemon mode'

    def handle(self, args):
        global _config
        bootstrapped_app = bootstrap.bootstrap_from_cli(_config, self.get_application_manager())
        app.run_application(_config, bootstrapped_app)


def get_default_config_path():
    for config_path in DEFAULT_CONFIG_LOCATIONS:
        if os.path.isfile(config_path):
            return config_path
    return None


def read_config_from_arguments() -> dict:
    known, unknown = supplementary_parser.parse_known_args()
    if known.config is None:
        config_path = get_default_config_path()
    else:
        config_path = known.config.name
        known.config.close()
    if config_path:
        CLI.print_info("Loaded config: " + os.path.realpath(config_path))
        CLI.print_info("")
        return bootstrap.read_config(config_path)
    else:
        return {}


def main():
    global _config
    logging.basicConfig(level=logging.DEBUG)
    _config = read_config_from_arguments()
    application = bootstrap.bootstrap_cli(_config)
    # Register system CLI commands
    application.cli_extensions.append(
        ('server', ServerRunCLIExtension)
    )
    # process CLI extensions
    for namespace, ext in application.cli_extensions:
        if namespace not in namespace_parsers.keys():
            p = module_parser.add_parser(namespace)
            namespace_parsers[namespace] = p.add_subparsers(title='module_cmd', dest='module_cmd')
        ext_parser = namespace_parsers[namespace]
        if ext.COMMAND_NAME is None:
            raise Exception(
                "Invalid CLI Extension: {}. COMMAND_NAME needs to be defined".format(ext.__class__.__name__))
        ext_subparser = ext_parser.add_parser(ext.COMMAND_NAME,
                                              help=ext.COMMAND_DESCRIPTION)
        ext.setup_parser(ext_subparser)
        ext_instance = ext(ext_subparser, application)
        ext_subparser.set_defaults(handler=ext_instance)

    gc.collect()
    args = parser.parse_args()
    if hasattr(args, "handler"):
        args.handler.handle(args)

if __name__ == '__main__':
    main()