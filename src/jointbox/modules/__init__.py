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

import logging
from jointbox.common.drivers import ModuleDiscoveryDriver
from jointbox.common.core import ModuleRegistry
from jointbox.modules.button import ButtonModule
from jointbox.modules.cli_mng import CliMngModule
from jointbox.modules.communication_bus import CommunicationBusModule
from jointbox.modules.dhtxx import DHTxxModule
from jointbox.modules.key_reader import KeyReaderModule
from jointbox.modules.pcf8574 import PCF8574Module
from jointbox.modules.logger_module import LoggerModule
from jointbox.modules.motion_sensor import MotionSensorModule
from jointbox.modules.onewire_thermometer import OneWireThermometerModule
from jointbox.modules.power_key import PowerKeyModule


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
        module_registry.register(DHTxxModule)
        module_registry.register(PCF8574Module)
        module_registry.register(KeyReaderModule)
