from random import random

from typing import Dict

from common.drivers import OneWireDriver
from common.errors import InvalidModuleError
from common.model import StateAwareModule, ParameterDef, Driver


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
