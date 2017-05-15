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

from typing import Dict

from common.drivers import OneWireDriver
from common.drivers.gpio import GPIODriver, GPIOMode
from common.errors import InvalidModuleError
from common.model import StateAwareModule, ParameterDef, Driver
from modules.dhtxx.dht11 import DHT11


class DHTxxModule(StateAwareModule):
    @staticmethod
    def typeid() -> int:
        return 0x0106

    @staticmethod
    def type_name() -> str:
        return 'DHTxx'

    def __init__(self, application, drivers: Dict[int, Driver]):
        super().__init__(application, drivers)
        self.gpio = 0
        self.temperature = None  # type: float
        self.humidity = None  # type: float
        self.__gpio_driver = drivers.get(GPIODriver.typeid())  # type: GPIODriver
        self.__dht11 = None  # type: DHT11

    def on_initialized(self):
        super().on_initialized()
        gpio_channel = self.__gpio_driver.new_channel(self.gpio, GPIOMode.READ)
        self.__dht11 = DHT11(gpio_channel)

    def step(self):
        try:
            result = self.__dht11.read()
        except Exception as e:
            self.logger.exception(str(e))
            return
        if result.is_valid():
            self.temperature = result.temperature
            self.humidity = result.humidity
            self.commit_state()
        else:
            self.logger.error("Failed to read data from DHTxx sensor on GPIO {}: Error code: {}"
                              .format(self.gpio, result.error_code))

    PARAMS = [
        ParameterDef('gpio', is_required=True)
    ]
    MINIMAL_ITERATION_INTERVAL = 5 * 60 * 1000
    STATE_FIELDS = ['temperature', 'humidity']
    REQUIRED_DRIVERS = [GPIODriver.typeid()]
    IN_BACKGROUND = True
