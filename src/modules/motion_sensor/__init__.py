import logging

from typing import List, Dict

from common.drivers import GPIODriver
from common.utils import capture_time
from common import validators
from common.model import DeviceModule, EventDef, ActionDef, ParameterDef, StateAwareModule, Driver

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
        self.__channel = self.__gpioDriver.new_channel(self.gpio, GPIODriver.GPIO_MODE_READ, pullup=self.invert)
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
