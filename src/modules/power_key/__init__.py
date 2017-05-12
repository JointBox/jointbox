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

from common.drivers import GPIODriver
from common.model import DeviceModule, EventDef, ActionDef, ParameterDef, StateAwareModule, Driver

ACTION_OFF = 0x010001
ACTION_ON = 0x010002
ACTION_TOGGLE = 0x010003
ACTION_SET_STATE = 0x010004


class PowerKeyModule(StateAwareModule):
    STATE_FIELDS = ['is_on']

    def __init__(self, application, drivers: Dict[int, Driver]):
        super().__init__(application, drivers)
        self.__logger = logging.getLogger('PowerKeyModule')
        self.__gpioDriver = drivers.get(GPIODriver.typeid())    # type: GPIODriver
        self.gpio = 0
        self.__channel = None   # type: GPIODriver.Channel

    @staticmethod
    def typeid() -> int:
        return 0x0100

    @staticmethod
    def type_name() -> str:
        return 'PowerKey'

    def on_initialized(self):
        self.__channel = self.__gpioDriver.new_channel(self.gpio, GPIODriver.GPIO_MODE_WRITE)

    def off(self, data=None, **kwargs):
        self.set_state(False)

    def on(self, data=None, **kwargs):
        self.set_state(True)

    def toggle(self, data=None, **kwargs):
        self.set_state(not self.is_on)

    def __action_set_state(self, data=None, **kwargs):
        # TODO: validate data!
        self.set_state(data)

    def set_state(self, state):
        self.is_on = state in [1, True, '1', 'true', 'on']

    @property
    def is_on(self) -> bool:
        return self.state.is_on

    @is_on.setter
    def is_on(self, val: bool):
        self.__channel.write(val)
        self.state.is_on = val
        self.commit_state()

    ACTIONS = [
        ActionDef(ACTION_OFF, 'off', off),
        ActionDef(ACTION_ON, 'on', on),
        ActionDef(ACTION_TOGGLE, 'toggle', toggle),
        ActionDef(ACTION_SET_STATE, 'state', __action_set_state),
    ]

    PARAMS = [
        ParameterDef('gpio', is_required=True)
    ]
    IN_LOOP = False
    REQUIRED_DRIVERS = [GPIODriver.typeid()]
