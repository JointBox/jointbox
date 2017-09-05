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

from common.drivers import I2cDriver
from common.drivers.key_reader import I2cKeyReaderDriver
from .i2c import Pn532I2c


class Np532KeyReaderDriver(I2cKeyReaderDriver):
    class Np532Device(I2cKeyReaderDriver.Device):

        def __init__(self, i2c_driver: I2cDriver, i2c_address: int, i2c_bus: int) -> None:
            super().__init__()
            self.np532I2c = Pn532I2c(i2c_driver, i2c_address, i2c_bus)
            #self.np532I2c.SAMconfigure()

        def read_key(self) -> List[int]:
            return self.np532I2c.read_mifare()

        def close(self):
            if self.np532I2c:
                self.np532I2c.close()

    def create_device(self, i2c_address: int, i2c_bus: int) -> Np532Device:
        return Np532KeyReaderDriver.Np532Device(self._i2c_driver, i2c_address, i2c_bus)