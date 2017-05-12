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

from argparse import ArgumentParser

from common.model import Module, CliExtension
from common import utils
from common.utils import CLI


class CoreDriversList(CliExtension):
    COMMAND_NAME = 'drivers:list'
    COMMAND_DESCRIPTION = 'Returns the list of the registered drivers'

    @classmethod
    def setup_parser(cls, parser: ArgumentParser):
        pass

    def handle(self, args):
        drivers = self.get_application_manager().drivers.values()
        for driver in drivers:
            CLI.print_data('* {} (id: {})'.format(driver.type_name(), utils.int_to_hex4str(driver.typeid())))


class CoreModulesList(CliExtension):
    COMMAND_NAME = 'modules:list'
    COMMAND_DESCRIPTION = 'Returns the list of discovered modules'

    @classmethod
    def setup_parser(cls, parser: ArgumentParser):
        pass

    def handle(self, args):
        modules = self.get_application_manager().get_module_registry().modules.values()
        for module in modules:
            CLI.print_data('* {} (id: {})'.format(module.type_name(), utils.int_to_hex4str(module.typeid())))


class CliMngModule(Module):
    CLI_NAMESPACE = 'core'
    CLI_EXTENSIONS = [
        CoreDriversList,
        CoreModulesList
    ]

    @staticmethod
    def typeid() -> int:
        return 0x0111

    @staticmethod
    def type_name() -> str:
        return 'CliMng'

