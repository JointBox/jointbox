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

from typing import Dict, Any

from common import validators, parse_utils
from common.drivers import I2cDriver
from common.drivers.gpio import GPIODriver, GPIOMode, GPIOResistorState, GPIOState
from common.errors import ConfigError
from common.model import ParameterDef, Driver, DeviceModule, ExternalRefHandler, Module
from argparse import ArgumentParser
from common.core import ApplicationManager
from common.model import CliExtension
from common.utils import CLI


class CommonPCF8574CliExtension(CliExtension):
    @classmethod
    def setup_parser(cls, parser: ArgumentParser):
        parser.add_argument('-b', '--bus', dest='bus', type=parse_utils.parse_int_str, required=False, default=0,
                            help='ID of the I2C bus. Should be an integer value. 0 by default.')
        parser.add_argument('-a', '--addr', dest='addr', type=parse_utils.parse_int_str, required=False, default=0,
                            help='ID of the I2C bus. Should be an integer value. 0 by default.')

    def __init__(self, parser: ArgumentParser, application: ApplicationManager):
        super().__init__(parser, application)
        self._pcf8574_module = PCF8574Module(application, application.drivers)

    def handle(self, args):
        self._pcf8574_module.i2c_bus = args.bus
        self._pcf8574_module.i2c_address = args.addr
        self._pcf8574_module.on_initialized()
        self._pcf8574_module.logger.info('Using driver: ' + str(self._pcf8574_module._i2c_driver))


class ReadPortCliExtension(CommonPCF8574CliExtension):
    COMMAND_NAME = 'read'
    COMMAND_DESCRIPTION = 'Reads state of all pins'

    def __init__(self, parser: ArgumentParser, application: ApplicationManager):
        super().__init__(parser, application)

    def handle(self, args):
        super().handle(args)
        val = self._pcf8574_module.read_port_value()
        CLI.print_data("{0:b}".format(val))


class WritePortCliExtension(CommonPCF8574CliExtension):
    COMMAND_NAME = 'write'
    COMMAND_DESCRIPTION = 'Sets state for each pin by given bitmask'

    def __init__(self, parser: ArgumentParser, application: ApplicationManager):
        super().__init__(parser, application)

    @classmethod
    def setup_parser(cls, parser: ArgumentParser):
        super().setup_parser(parser)
        parser.add_argument('val', type=str,
                            help='Binary string representing target state of the pins. '
                                 'Should be exactly 8 bits. Example: 01011101')

    def handle(self, args):
        super().handle(args)
        val_str = args.val
        if len(val_str) != 8:
            raise ValueError('val should be exactly 8 bits')
        try:
            val = int(val_str, 2)
        except ValueError:
            raise ValueError('Invalid val value. It should be binary string (contains only 0 or 1)')
        self._pcf8574_module.logger.info("Sending 0x{0:x} to i2c device".format(val))
        self._pcf8574_module.write_port_value(val)


class PCF8574Module(DeviceModule, ExternalRefHandler):
    @staticmethod
    def typeid() -> int:
        return 0x0107

    @staticmethod
    def type_name() -> str:
        return 'PCF8574'

    def __init__(self, application, drivers: Dict[int, Driver]):
        super().__init__(application, drivers)
        self.i2c_bus = 0
        self.i2c_address = 0
        self._i2c_driver = drivers.get(I2cDriver.typeid())  # type: I2cDriver
        self._i2c_bus = None  # type: I2cDriver.I2cBus

    def on_initialized(self):
        super().on_initialized()
        self._i2c_bus = self._i2c_driver.get_bus(self.i2c_bus)

    def on_before_destroyed(self):
        if self._i2c_bus is not None:
            self._i2c_bus.close()

    def read_port_value(self) -> int:
        """
        Read state of the port (all 8 pins). 
        :return: Byte representing pins state
        """
        return self._i2c_bus.read_byte(self.i2c_address, 0)

    def write_port_value(self, value):
        assert 0 <= value <= 255, 'value should be exactly 1 byte (allowed range 0-255)'
        self._i2c_bus.write_byte_data(self.i2c_address, 0, value)

    def get_pin_state(self, pin_num: int) -> int:
        return self.read_port_value() & 1 << 7 - pin_num

    def set_pin_state(self, pin_num: int, value: int):
        current_port_state = self._i2c_bus.read_byte(self.i2c_address, 0)
        bit = 1 << 7 - pin_num
        new_state = current_port_state | bit if value else current_port_state & (~bit & 0xff)
        self._i2c_bus.write_byte_data(self.i2c_address, new_state, 0)

    def handle_external_ref(self, source: [Driver, Module], args_str: str, ref_str: str) -> Any:
        if not isinstance(source, GPIODriver):
            raise ConfigError("PCF8574Module supports only GPIO driver references.")

        pass

    PARAMS = [
        ParameterDef('i2c_bus', is_required=False, validators=validators.integer),
        ParameterDef('i2c_address', is_required=True, validators=validators.integer)
    ]
    REQUIRED_DRIVERS = [I2cDriver.typeid()]
    IN_LOOP = False
    CLI_NAMESPACE = 'pcf8574'
    CLI_EXTENSIONS = (
        ReadPortCliExtension,
        WritePortCliExtension,
    )


class PCF8574toGPIOBridge(GPIODriver.Channel):
    def set_mode(self, direction: GPIOMode, resistor: GPIOResistorState = GPIOResistorState.UNKNOWN):
        pass

    def __init__(self, pcf8574: PCF8574Module):
        super().__init__()
        self.pcf8574 = pcf8574

    def write(self, state: [GPIOState, int, bool]):
        super().write(state)

    def read(self, reverse=False) -> GPIOState:
        return super().read(reverse)
