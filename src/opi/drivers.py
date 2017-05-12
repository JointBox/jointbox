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
from common.drivers import GPIODriver
from common.errors import SimpleException


class OpiH3GPIODriver(GPIODriver):
    class OpiH3Channel(GPIODriver.Channel):

        def __init__(self, gpio, pin, mode, pullup=True):
            self.__gpio = gpio
            self.pin = pin
            self.__gpio.setcfg(pin, self.__gpio.INPUT if mode == GPIODriver.GPIO_MODE_READ else self.__gpio.OUTPUT)
            if pullup is not None:
                self.__gpio.pullup(pin, self.__gpio.PULLUP if pullup else self.__gpio.PULLDOWN)

        def write(self, state: [int, bool]):
            self.__gpio.output(self.pin, not state)

        def read(self, reverse=False) -> int:
            if reverse:
                return int(not self.__gpio.input(self.pin))
            else:
                return self.__gpio.input(self.pin)

    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__name__)

    def on_initialized(self, application):
        super().on_initialized(application)
        try:
            from pyA20.gpio import gpio
            from pyA20.gpio import port
            self.__gpio = gpio
            self.__port = port
        except Exception as e:
            raise SimpleException("Unable to load GPIO driver. Most likely this is because you need administrative "
                                  "permissions.", e)
        gpio.init()

    def new_channel(self, pin: [str, int], mode: int, pullup=True) -> OpiH3Channel:
        try:
            pin = getattr(self.__port, pin)
        except Exception as e:
            raise SimpleException("Unable to use pin " + str(pin), e)
        channel = OpiH3GPIODriver.OpiH3Channel(self.__gpio, pin, mode, pullup)
        return channel
