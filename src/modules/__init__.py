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
from common.drivers import ModuleDiscoveryDriver
from common.core import ModuleRegistry
from modules.button import ButtonModule
from modules.cli_mng import CliMngModule
from modules.communication_bus import CommunicationBusModule
from modules.dhtxx import DHTxxModule
from modules.gpio_expander import PCF8574Module
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
        module_registry.register(DHTxxModule)
        module_registry.register(PCF8574Module)
