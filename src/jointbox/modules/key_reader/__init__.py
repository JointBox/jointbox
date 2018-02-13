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

from jointbox.common import validators
from jointbox.common.drivers import I2cDriver
from jointbox.common.drivers.key_reader import I2cKeyReaderDriver
from jointbox.common.model import DeviceModule, Driver, ParameterDef


class KeyReaderModule(DeviceModule):
    @staticmethod
    def type_name() -> str:
        return "SmartCardReader"

    @staticmethod
    def typeid() -> int:
        return 0x108

    def __init__(self, application, drivers: Dict[int, Driver]):
        super().__init__(application, drivers)
        self.i2c_bus = 0
        self.i2c_address = 0
        self.__i2c_driver = drivers.get(I2cDriver.typeid())
        self.__key_reader_driver = drivers.get(I2cKeyReaderDriver.typeid())  # type: I2cKeyReaderDriver
        self.__device = None  # type: I2cKeyReaderDriver.Device

    def on_initialized(self):
        super().on_initialized()
        self.__device = self.__key_reader_driver.create_device(self.i2c_address, self.i2c_bus)

    def step(self):
        key = self.__device.read_key()
        print("KEY: " + str(key))

    REQUIRED_DRIVERS = [I2cDriver.typeid(), I2cKeyReaderDriver.typeid()]
    MINIMAL_ITERATION_INTERVAL = 5000
    PARAMS = [
        ParameterDef('i2c_bus', is_required=False, validators=(validators.integer,)),
        ParameterDef('i2c_address', is_required=True, validators=(validators.integer,))
    ]
