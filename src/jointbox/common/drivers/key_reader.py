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

from typing import List

from jointbox.common.drivers import I2cDriver
from jointbox.common.model import Driver


class I2cKeyReaderDriver(Driver):
    class Device:
        def read_key(self) -> List[int]:
            pass

        def close(self):
            pass

    @staticmethod
    def type_name() -> str:
        return "KeyReader"

    @staticmethod
    def typeid() -> int:
        return 0x1006

    def __init__(self):
        super().__init__()
        self._devices = []  # type: List[KeyReaderDriver.Device]
        self._i2c_driver = None # type: I2cDriver

    def on_initialized(self, application):
        super().on_initialized(application)
        self._i2c_driver = application.get_driver(I2cDriver.typeid())

    def on_before_unloaded(self, application):
        super().on_before_unloaded(application)
        for x in self._devices:
            x.close()

    def create_device(self, i2c_address: int, i2c_bus: int) -> Device:
        raise NotImplementedError()

    def new_device(self, i2c_address: int, i2c_bus: int) -> Device:
        device = self.create_device(i2c_address, i2c_bus)
        self._devices.append(device)
