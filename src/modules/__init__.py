import logging
from common.drivers import ModuleDiscoveryDriver
from common.core import ModuleRegistry
from modules.button import ButtonModule
from modules.cli_mng import CliMngModule
from modules.communication_bus import CommunicationBusModule
from modules.logger_module import LoggerModule
from modules.motion_sensor import MotionSensorModule
from modules.onewire_thermometer import OneWireThermometerModule
from modules.power_key import PowerKeyModule


class StandardModulesOnlyDriver(ModuleDiscoveryDriver):

    def __init__(self):
        super().__init__()
        self.__logger = logging.getLogger('StandardModulesOnlyDriver')

    def discover_modules(self, module_registry: ModuleRegistry):
        self.__logger.debug("Do discovery!")
        module_registry.register(CliMngModule)
        module_registry.register(PowerKeyModule)
        module_registry.register(LoggerModule)
        module_registry.register(CommunicationBusModule)
        module_registry.register(OneWireThermometerModule)
        module_registry.register(ButtonModule)
        module_registry.register(MotionSensorModule)
