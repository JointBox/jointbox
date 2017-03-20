from typing import List, Callable

from .model import Driver


class GPIODriver(Driver):
    GPIO_MODE_READ = 0
    GPIO_MODE_WRITE = 1

    GPIO_RESISTOR_PULLUP = 0
    GPIO_RESISTOR_PULLDOWN = 1

    class Channel(object):
        def write(self, state: [int, bool]):
            pass

        def read(self, reverse=False) -> int:
            return 0

        def mode(self):
            return GPIODriver.GPIO_MODE_READ

        def set(self):
            self.write(True)

        def reset(self):
            self.write(False)

    @staticmethod
    def typeid() -> int:
        return 0x1001

    @staticmethod
    def type_name() -> str:
        return 'GPIO'

    def cleanup(self):
        """
        Dispose all system resources related to the GPIO subsystem and resets GPIO state
        """
        pass

    def new_channel(self, pin: [str, int], direction: int, pullup=True) -> Channel:
        pass


class ModuleDiscoveryDriver(Driver):
    @staticmethod
    def typeid() -> int:
        return 0x1002

    @staticmethod
    def type_name() -> str:
        return 'ModuleDiscovery'

    def discover_modules(self, module_registry):
        pass


class DataChannelDriver(Driver):
    class Channel(object):
        @staticmethod
        def noop(*args, **kwargs):
            pass

        def __init__(self, connection_options: dict):
            self.on_data_received = self.noop
            self.on_error = self.noop
            self.on_connect_first_time = self.noop
            self.on_connect = self.noop

        def is_connected(self) -> bool:
            return False

        def connect(self):
            pass

        def disconnect(self):
            pass

        def send(self, destination: str, data):
            pass

        def subscribe(self, topic: str):
            pass

        def step(self):
            pass

        def dispose(self):
            pass

    @staticmethod
    def typeid() -> int:
        return 0x1003

    @staticmethod
    def type_name() -> str:
        return 'CommunicationBus'

    def new_channel(self, connection_options: dict) -> Channel:
        """

        :param connection_options:
        :return:
        """
        pass


class OneWireDriver(Driver):
    @staticmethod
    def typeid() -> int:
        return 0x1004

    @staticmethod
    def type_name() -> str:
        return 'OneWire'

    def device_exists(self, device_name) -> bool:
        return device_name in self.get_available_devices()

    def get_available_devices(self) -> List[str]:
        pass

    def read_temperature(self, device_name: str) -> float:
        pass
