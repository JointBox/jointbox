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

import os

from typing import List

from common.drivers import OneWireDriver
from common.errors import SimpleException


class SysfsOneWireDriverError(SimpleException):
    pass


class SysfsOneWireDriver(OneWireDriver):
    def __init__(self):
        super().__init__()
        self.fs_root = '/sys/bus/w1'
        self.__devices_dir = ''

    def on_initialized(self, application):
        self.__devices_dir = os.path.join(self.fs_root, 'devices')
        try:
            self.logger.debug('Available devices: ' + str(self.get_available_devices()))
        except Exception as e:
            raise Exception("w1-gpio module is not loaded or base sysfs path is invalid")

    def __parse_raw_temperature_data(self, raw_data) -> [bool, float]:
        '''
        :param raw_data:
        :return: False if CRC is not valid, temperature in Celsiums otherwise
        '''
        if raw_data[0].strip()[-3:] != 'YES':
            return False
        equals_pos = raw_data[1].find('t=')
        # If the '=' is found, convert the rest of the line after the
        # '=' into degrees Celsius, then degrees Fahrenheit
        if equals_pos != -1:
            temp_string = raw_data[1][equals_pos + 2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c
        else:
            raise ValueError("Data output not recognized")

    def read_temperature(self, device_name: str) -> float:
        device_path = os.path.join(self.__devices_dir, str(device_name))
        if not os.path.exists(device_path):
            raise ValueError("W1 Device {} doesn't exist".format(device_name))
        try:
            with open(os.path.join(device_path, 'w1_slave'), 'r') as f:
                temperature = self.__parse_raw_temperature_data(f.readlines())
                if not temperature:
                    raise ValueError("Invalid CRC")
                return temperature
        except Exception as e:
            raise SysfsOneWireDriverError("Unable to read temperature from DS18B20 device {}: " + str(e), ex=e)

    def get_available_devices(self) -> List[str]:
        return [os.path.basename(x) for x in os.listdir(self.__devices_dir)]
