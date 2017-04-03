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

