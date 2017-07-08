from typing import Dict

from common import validators
from common.drivers import I2cDriver
from common.drivers.key_reader import I2cKeyReaderDriver
from common.model import DeviceModule, Driver, ParameterDef


class KeyReaderModule(DeviceModule):
    @staticmethod
    def type_name() -> str:
        return "SmartCardReader"

    @staticmethod
    def typeid() -> int:
        return 0x108

    def __init__(self, application, drivers: Dict[int, Driver]):
        super().__init__(application, drivers)
        self.i2c_bus = 0
        self.i2c_address = 0
        self.__i2c_driver = drivers.get(I2cDriver.typeid())
        self.__key_reader_driver = drivers.get(I2cKeyReaderDriver.typeid())  # type: I2cKeyReaderDriver
        self.__device = None  # type: I2cKeyReaderDriver.Device

    def on_initialized(self):
        super().on_initialized()
        self.__device = self.__key_reader_driver.create_device(self.i2c_address, self.i2c_bus)

    def step(self):
        key = self.__device.read_key()
        print("KEY: " + str(key))

    REQUIRED_DRIVERS = [I2cDriver.typeid(), I2cKeyReaderDriver.typeid()]
    MINIMAL_ITERATION_INTERVAL = 5000
    PARAMS = [
        ParameterDef('i2c_bus', is_required=False, validators=(validators.integer,)),
        ParameterDef('i2c_address', is_required=True, validators=(validators.integer,))
    ]
