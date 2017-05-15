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

from common.drivers.gpio import GPIODriver, GPIOResistorState, GPIOMode
from common.utils import capture_time
from common import validators
from common.model import DeviceModule, EventDef, ActionDef, ParameterDef, StateAwareModule, Driver

RELEASED = 0
PRESSED = 1

EVENT_CLICK = 0x010401
EVENT_LONG_CLICK = 0x010402
EVENT_DOUBLE_CLICK = 0x010403


class ButtonModule(DeviceModule):
    def __init__(self, application, drivers: Dict[int, Driver]):
        super().__init__(application, drivers)
        self.__logger = logging.getLogger('ButtonModule')
        self.__gpioDriver = drivers.get(GPIODriver.typeid())  # type: GPIODriver
        self.gpio = 0
        self.handle_long_click = False
        self.handle_double_click = False
        self.long_click_duration = 1000
        self.double_click_duration = 400
        self.pullup = True
        self.__channel = None  # type: GPIODriver.Channel
        self.__wait_until_released = False
        self.__prev_state = RELEASED
        self.__click_time = 0
        self.__pressed_time = 0
        self.__released_time = 0

    @staticmethod
    def typeid() -> int:
        return 0x0104

    @staticmethod
    def type_name() -> str:
        return 'Button'

    @property
    def ignore_complex_events(self):
        return not self.handle_long_click and not self.handle_double_click

    def on_initialized(self):
        self.__channel = self.__gpioDriver.new_channel(self.gpio, GPIOMode.READ,
                                                       GPIOResistorState.from_pullup_bool(self.pullup))

    def __register_new_state(self, state):
        if state != self.__prev_state:
            if self.__prev_state == RELEASED:
                self.__pressed_time = capture_time()
            else:
                self.__released_time = capture_time()

    def step(self):
        state = self.__channel.read(self.pullup)
        if self.__wait_until_released:
            if state == RELEASED:
                self.__wait_until_released = False
            else:
                return
        self.__register_new_state(state)
        if self.handle_long_click and state == PRESSED:
            if self.__pressed_time > 0 and capture_time() - self.__pressed_time >= self.long_click_duration:
                self.__pressed_time = 0
                self.__released_time = 0
                self.__prev_state = RELEASED
                self.__wait_until_released = True
                self.emit(EVENT_LONG_CLICK)
                return
        if self.__prev_state == PRESSED and state == RELEASED:
            if self.handle_double_click:
                if self.__click_time > 0 and capture_time() - self.__click_time <= self.double_click_duration:
                    self.__pressed_time = 0
                    self.__released_time = 0
                    self.__prev_state = RELEASED
                    self.__click_time = 0
                    self.emit(EVENT_DOUBLE_CLICK)
                    return
                elif self.__click_time == 0:
                    self.__click_time = capture_time()
                else:
                    self.emit(EVENT_CLICK)
            else:
                self.emit(EVENT_CLICK)
        # Reset click counter on timeout
        if state == RELEASED and self.handle_double_click and self.__click_time > 0 \
                and capture_time() - self.__click_time > self.double_click_duration:
            self.__click_time = 0
            self.emit(EVENT_CLICK)
        self.__prev_state = state

    PARAMS = [
        ParameterDef('gpio', is_required=True),
        ParameterDef('pullup', validators=(validators.boolean,)),
        ParameterDef('handle_long_click', validators=(validators.boolean,)),
        ParameterDef('handle_double_click', validators=(validators.boolean,)),
        ParameterDef('long_click_duration', validators=(validators.integer,)),
        ParameterDef('double_click_duration', validators=(validators.integer,)),
    ]
    EVENTS = [
        EventDef(EVENT_CLICK, 'click'),
        EventDef(EVENT_LONG_CLICK, 'long_click'),
        EventDef(EVENT_DOUBLE_CLICK, 'double_click'),
    ]
    MINIMAL_ITERATION_INTERVAL = 50
    REQUIRED_DRIVERS = [GPIODriver.typeid()]
