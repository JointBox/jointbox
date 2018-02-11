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
from jointbox.common.drivers.gpio import GPIODriver, GPIOMode, GPIOResistorState
from jointbox.common.errors import SimpleException

__SUNXI_GPA = 0
__SUNXI_GPB = 32
__SUNXI_GPC = 64
__SUNXI_GPD = 96
__SUNXI_GPE = 128
__SUNXI_GPF = 160
__SUNXI_GPG = 192
__SUNXI_GPH = 224
__SUNXI_GPI = 256
__SUNXI_GPJ = 288
__SUNXI_GPK = 320
__SUNXI_GPL = 352
__SUNXI_GPM = 384
__SUNXI_GPN = 448
__SUNXI_GPO = 448 + 32

# SOURCE: https://github.com/duxingkei33/orangepi_PC_gpio_pyH3/blob/master/pyA20/gpio/gpio_lib.h
__GPIO_MAPPING_LIST = (
    ("PA12", __SUNXI_GPA + 12, 3),
    ("PA11", __SUNXI_GPA + 11, 5),
    ("PA6", __SUNXI_GPA + 6, 7),
    ("PA1", __SUNXI_GPA + 1, 11),
    ("PA2", __SUNXI_GPA + 2, 22),
    ("PA0", __SUNXI_GPA + 0, 13),
    ("PA3", __SUNXI_GPA + 3, 15),
    ("PA19", __SUNXI_GPA + 19, 27),
    ("PA7", __SUNXI_GPA + 7, 29),
    ("PA8", __SUNXI_GPA + 8, 31),
    ("PA9", __SUNXI_GPA + 9, 33),
    ("PA10", __SUNXI_GPA + 10, 35),
    ("PA20", __SUNXI_GPA + 20, 37),
    ("PA21", __SUNXI_GPA + 21, 26),
    ("PA18", __SUNXI_GPA + 18, 28),
    ("PA13", __SUNXI_GPA + 13, 8),
    ("PA14", __SUNXI_GPA + 14, 10),

    ("PC0", __SUNXI_GPC + 0, 19),
    ("PC1", __SUNXI_GPC + 1, 21),
    ("PC2", __SUNXI_GPC + 2, 23),
    ("PC4", __SUNXI_GPC + 4, 16),
    ("PC7", __SUNXI_GPC + 7, 18),
    ("PC3", __SUNXI_GPC + 3, 24),

    ("PD14", __SUNXI_GPD + 14, 12),

    ("PG8", __SUNXI_GPG + 8, 32),
    ("PG9", __SUNXI_GPG + 9, 36),
    ("PG6", __SUNXI_GPG + 6, 38),
    ("PG7", __SUNXI_GPG + 7, 40),

)

_GPIO_PORT_MAPPING = {}
_GPIO_IDX_MAPPING = {}

for port, offset, gpio_id in __GPIO_MAPPING_LIST:
    _GPIO_IDX_MAPPING[gpio_id] = offset
    _GPIO_PORT_MAPPING[port] = offset


class OpiH3GPIODriver(GPIODriver):
    class OpiH3Channel(GPIODriver.Channel):

        def __init__(self, gpio, pin, direction: GPIOMode,
                     resistor_mode: GPIOResistorState = GPIOResistorState.PULLUP):
            super().__init__()
            self.__gpio = gpio
            self.pin = pin
            self.set_mode(direction, resistor_mode)

        def write(self, state: [int, bool]):
            self.__gpio.output(self.pin, not state)

        def read(self, reverse=False) -> int:
            if reverse:
                return int(not self.__gpio.input(self.pin))
            else:
                return self.__gpio.input(self.pin)

        def set_mode(self, direction: GPIOMode, resistor=GPIOResistorState.UNKNOWN):
            self._mode = direction
            self.__gpio.setcfg(self.pin,
                               self.__gpio.INPUT if direction == GPIOMode.READ else self.__gpio.OUTPUT)
            if resistor != GPIOResistorState.UNKNOWN:
                self.__gpio.pullup(self.pin,
                                   self.__gpio.PULLUP if resistor == GPIOResistorState.PULLUP else self.__gpio.PULLDOWN)

    def __init__(self):
        super().__init__()
        self.__logger = logging.getLogger(self.__class__.__name__)

    def on_initialized(self, application):
        super().on_initialized(application)
        try:
            from pyA20.gpio import gpio
            self.__gpio = gpio
        except Exception as e:
            raise SimpleException("Unable to load GPIO driver. Most likely this is because you need administrative "
                                  "permissions.", e)
        gpio.init()

    def __get_gpio_offset(self, name_or_num: [str, int]) -> int:
        try:
            if isinstance(name_or_num, str):
                return _GPIO_PORT_MAPPING[name_or_num]
            elif isinstance(name_or_num, int):
                return _GPIO_IDX_MAPPING[name_or_num]
            else:
                raise SimpleException("Invalid pin identifier: " + name_or_num)
        except KeyError as e:
            raise SimpleException("Pin {} doesn't exist".format(name_or_num))

    def new_channel(self, pin: [str, int], direction: GPIOMode,
                    resistor_mode: GPIOResistorState = GPIOResistorState.PULLUP) -> OpiH3Channel:
        pin = self.resolve_pin_name(pin)
        if isinstance(pin, GPIODriver.Channel):
            return pin
        try:
            pin = self.__get_gpio_offset(pin)
        except Exception as e:
            raise SimpleException("Unable to use pin " + str(pin), e)
        channel = OpiH3GPIODriver.OpiH3Channel(self.__gpio, pin, direction, resistor_mode)
        return channel
