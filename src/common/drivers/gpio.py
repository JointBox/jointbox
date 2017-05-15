from enum import IntEnum, Enum

import re

from common.errors import ConfigError
from common.model import Driver, ExternalRefHandler

PINREF_REGEX = re.compile('#([\w\d_\-]+)/(.*)$', re.IGNORECASE)


class GPIOState(IntEnum):
    HIGH = 1
    LOW = 0


class GPIOMode(IntEnum):
    READ = 0
    WRITE = 1


class GPIOResistorState(Enum):
    UNKNOWN = None
    PULLUP = 0
    PULLDOWN = 1

    @staticmethod
    def from_pullup_bool(val):
        """
        Assumes that TRUE means pullup, FALSE - pulldown, None - Unknown
        :return: 
        """
        if val is None:
            return GPIOResistorState.UNKNOWN
        elif val:
            return GPIOResistorState.PULLUP
        else:
            return GPIOResistorState.PULLDOWN


class GPIODriver(Driver):

    class Channel:
        def write(self, state: [GPIOState, int, bool]):
            pass

        def read(self, reverse=False) -> GPIOState:
            return GPIOState.LOW

        def mode(self):
            return self._mode

        def set_mode(self, direction: GPIOMode, resistor: GPIOResistorState = GPIOResistorState.UNKNOWN):
            raise NotImplementedError()

        def set(self):
            self.write(True)

        def reset(self):
            self.write(False)

        def __init__(self):
            self._mode = GPIOMode.READ

    def __init__(self):
        super().__init__()
        self._application_manager = None  # type: common.core.ApplicationManager

    @staticmethod
    def typeid() -> int:
        return 0x1001

    @staticmethod
    def type_name() -> str:
        return 'GPIO'

    def on_initialized(self, application):
        super().on_initialized(application)
        self._application_manager = application

    def cleanup(self):
        """
        Dispose all system resources related to the GPIO subsystem and resets GPIO state
        """
        pass

    def _handle_pinref_string(self, pin_ref: str) -> [None, Channel]:
        """
        Pin ref string looks like this: #my_module1/1
        Where my_module - is id of the module instance which implements ExternalRefHandler interface. 
        This handler should be able to produce initialized GPIO channel (instance of GPIODriver.Channel) 
              1 - actual GPIO number
        :param pin_ref: 
        :return: 
        """
        match = PINREF_REGEX.match(pin_ref)
        if match is None:
            return None
        device_name, pin_arg = match.groups()
        device = self._application_manager.get_device_by_name(device_name)
        if device is None:
            raise ConfigError("Invalid pinref \'{}\'. Device {} not found".format(pin_ref, device_name))
        if isinstance(device, ExternalRefHandler):
            try:
                channel = device.handle_external_ref(pin_arg, pin_arg, pin_ref)
                if channel is not None and not isinstance(channel, GPIODriver.Channel):
                    raise Exception("Invalid result from ref handler {}. Expected GPIODriver.Channel but got {}".format(
                        device.__class__.__name__, channel.__class__.__name__))
            except Exception as e:
                raise ConfigError("Unable to handle external ref: " + str(e), e)
        else:
            raise ConfigError("Invalid pinref \'{}\'. Target device should implement ExternalRefHandler"
                              .format(pin_ref))
        return None

    def __canonize_pin_name(self, pin: [str, int]) -> [str, int, Channel]:
        """
        Parses string defining external reference for GPIO channel builder.
        It may either convert given pin number value to canonical form supported by GPIO library or 
        return an instance of initialized channel
        :return: 
        """
        result = None
        if isinstance(pin, str) and pin.startswith('#'):
            self._handle_pinref_string(pin)
        else:
            pass  # implement other transformation logic here
        if result is not None:
            return result
        else:
            return pin

    def new_channel(self, pin: [str, int], direction: GPIOMode,
                    resistor_mode: GPIOResistorState = GPIOResistorState.PULLUP) -> Channel:
        pass
