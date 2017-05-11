import os
from typing import Tuple, List
from smbus2 import SMBus
from common.drivers import I2cDriver as BaseI2cDriver
from common.errors import InvalidDriverError

DEV_DIR = '/dev'
I2C_DEV_PREFIX = 'i2c-'


class I2cDriver(BaseI2cDriver):
    class I2cBus(BaseI2cDriver.I2cBus):

        def __init__(self, bus_id):
            super().__init__(bus_id)
            try:
                self.bus = SMBus(bus_id)
            except Exception as e:
                raise InvalidDriverError(
                    'Unable to initialize i2c connection with bus {}. Check if i2c bus is avalable.'.format(bus_id), e)

        def close(self):
            if self.bus is not None:
                self.bus.close()

        def read_byte(self, addr: int, register: int) -> int:
            return self.bus.read_byte_data(addr, register)

        def read_word(self, addr: int, register: int) -> int:
            return self.bus.read_word_data(addr, register)

        def read_block(self, addr: int, register, length: int) -> List[int]:
            return self.bus.read_i2c_block_data(addr, register, length)

        def write_byte_data(self, addr, register, value):
            self.bus.write_byte_data(addr, register, value)

        def write_word_data(self, addr, register, value):
            self.bus.write_word_data(addr, register, value)

        def write_block_data(self, addr, register, data):
            self.bus.write_i2c_block_data(addr, register, data)

    def __init__(self):
        super().__init__()
        self.buses = {}

    def list_buses(self) -> List[Tuple[str, int]]:
        result = []
        for dev_name in os.listdir(DEV_DIR):
            if dev_name.startswith(I2C_DEV_PREFIX):
                result.append((dev_name, int(dev_name.replace(I2C_DEV_PREFIX, ''))))
        return result

    def get_bus(self, bus_id=None):
        if bus_id is None:
            bus_id = self.default_bus
        if bus_id in self.buses:
            return self.buses[bus_id]
        else:
            bus = self.I2cBus(bus_id)
            self.buses[bus_id] = bus

    def on_before_unloaded(self, application):
        for bus_id, bus in self.buses.items():
            self.logger.info("Unloading I2C bus " + bus_id)
            bus.close()


