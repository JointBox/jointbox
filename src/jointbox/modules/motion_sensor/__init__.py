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

from typing import List, Dict

from jointbox.common.drivers.gpio import GPIODriver, GPIOResistorState, GPIOMode
from jointbox.common.utils import capture_time
from jointbox.common import validators
from jointbox.common.model import DeviceModule, EventDef, ActionDef, ParameterDef, StateAwareModule, Driver

EVENT_MOTION_DETECTED = 0x010501
EVENT_NO_MOTION = 0x010502


class MotionSensorModule(DeviceModule):
    """
    HC-SR501 PIR MOTION DETECTOR https://www.mpja.com/download/31227sc.pdf
    """

    def __init__(self, application, drivers: Dict[int, Driver]):
        super().__init__(application, drivers)
        self.__gpioDriver = drivers.get(GPIODriver.typeid())  # type: GPIODriver
        self.gpio = 0
        self.MOTION_DETECTED_LEVEL = 1
        self.invert = False
        self.__channel = None  # type: GPIODriver.Channel
        self.__prev_state = 0

    @staticmethod
    def typeid() -> int:
        return 0x0105

    @staticmethod
    def type_name() -> str:
        return 'MotionSensor'

    def on_initialized(self):
        self.__channel = self.__gpioDriver.new_channel(self.gpio, GPIOMode.READ,
                                                       GPIOResistorState.from_pullup_bool(self.invert))
        self.MOTION_DETECTED_LEVEL = 0 if self.invert else 1

    def step(self):
        state = self.__channel.read(self.invert)
        if state != self.__prev_state:
            self.logger.debug('State changed: ' + str(state))
            if state == self.MOTION_DETECTED_LEVEL:
                self.emit(EVENT_MOTION_DETECTED)
                self.logger.debug('Motion detected')
            else:
                self.emit(EVENT_NO_MOTION)
                self.logger.debug('No motion')
            self.__prev_state = state

    PARAMS = [
        ParameterDef('gpio', is_required=True),
        ParameterDef('invert', validators=(validators.boolean,)),
    ]
    EVENTS = [
        EventDef(EVENT_MOTION_DETECTED, 'motion_detected'),
        EventDef(EVENT_NO_MOTION, 'no_motion'),
    ]
    MINIMAL_ITERATION_INTERVAL = 100
    REQUIRED_DRIVERS = [GPIODriver.typeid()]
