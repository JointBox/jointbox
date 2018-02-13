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

from jointbox.common.drivers import OneWireDriver
from jointbox.common.errors import InvalidModuleError
from jointbox.common.model import StateAwareModule, ParameterDef, Driver


class OneWireThermometerModule(StateAwareModule):
    @staticmethod
    def typeid() -> int:
        return 0x0103

    @staticmethod
    def type_name() -> str:
        return '1wireThermometer'

    def __init__(self, application, drivers: Dict[int, Driver]):
        super().__init__(application, drivers)
        self.device_id = None  # type: str
        self.__update_interval = self.MINIMAL_ITERATION_INTERVAL
        self.__w1 = drivers.get(OneWireDriver.typeid())     # type: OneWireDriver

    def step(self):
        t = self.__w1.read_temperature(self.device_id)
        self.logger.debug("Temperature: {} C".format(t))
        self.state.temperature = t
        self.commit_state()

    @property
    def update_interval(self):
        return self.MINIMAL_ITERATION_INTERVAL

    @update_interval.setter
    def update_interval(self, value:[str,int]):
        if isinstance(value, int):
            self.MINIMAL_ITERATION_INTERVAL = value
        else:
            raise InvalidModuleError("OneWireThermometerModule: update_interval should be "
                                     "integer value representing time in millis")

    STATE_FIELDS = ['temperature']
    ACTIONS = []
    PARAMS = [
        ParameterDef('device_id', is_required=True),
        ParameterDef('update_interval', is_required=False),
    ]
    MINIMAL_ITERATION_INTERVAL = 5 * 60 * 1000
    REQUIRED_DRIVERS = [OneWireDriver.typeid()]
    IN_BACKGROUND = True
