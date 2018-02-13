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

from jointbox.common.drivers.gpio import GPIOMode, GPIODriver, GPIOResistorState, GPIOState


class PCF8574toGPIOBridge(GPIODriver.Channel):
    def __init__(self, pin: int, pcf8574):
        """
        :type pcf8574: modules.pcf8574.PCF8574Module 
        """
        super().__init__()
        self.pin = pin
        self.pcf8574 = pcf8574  # type: modules.pcf8574.PCF8574Module

    def set_mode(self, direction: GPIOMode, resistor: GPIOResistorState = GPIOResistorState.UNKNOWN):
        # 1. No need to switch mode
        # 2. Resistor is always PULL UP
        if resistor == GPIOResistorState.PULLDOWN:
            raise ValueError("PCF8574 doesn't support PULL DOWN resistor.")

    def write(self, state: [GPIOState, int, bool]):
        self.pcf8574.set_pin_state(self.pin, state)

    def read(self, reverse=False) -> GPIOState:
        return GPIOState(self.pcf8574.get_pin_state(self.pin))
