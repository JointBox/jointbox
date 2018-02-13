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

from argparse import ArgumentParser

from typing import List, Tuple

from jointbox.common.utils import CLI
from ..model import Driver, CliExtension

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
    class ScanLineCliExtension(CliExtension):
        COMMAND_NAME = "scan"
        COMMAND_DESCRIPTION = "Scans 1-wire line and outputs all identified devices"

        def handle(self, args):
            try:
                devices = self.get_application_manager().get_driver(OneWireDriver.typeid()).get_available_devices()
                for d in devices:
                    CLI.print_data("* {}".format(d))
            except Exception as e:
                CLI.print_error("Unable to scan 1-wire line: " + str(e))

    CLI_NAMESPACE = 'w1'
    CLI_EXTENSIONS = [
        ScanLineCliExtension
    ]

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


class I2cDriver(Driver):
    class ListBusesCliExtension(CliExtension):
        COMMAND_NAME = 'buses'
        COMMAND_DESCRIPTION = 'Returns the list of avaliable I2C buses'

        def handle(self, args):
            driver = self.get_application_manager().get_driver(I2cDriver.typeid())  # type: I2cDriver
            buses = driver.list_buses()
            if len(buses) == 0:
                CLI.print_info("There are no i2c buses available")
                return
            CLI.print_data('  name\tid')
            for name, id in buses:
                CLI.print_data('* {}\t{}'.format(name, id))

    class ScanBusCliExtension(CliExtension):
        COMMAND_NAME = 'scan'
        COMMAND_DESCRIPTION = 'Scans given i2c bus and returns the list of addresses discovered'

        @classmethod
        def setup_parser(cls, parser: ArgumentParser):
            parser.add_argument('-b', '--bus', dest='bus', type=int, required=False, default=0,
                                help='ID of the I2C bus. Should be an integer value. 0 by default.')

    class I2cBus:

        def __init__(self, bus_id: int):
            super().__init__()

        def read_byte(self, addr: int, register: int) -> int:
            """
            Read single byte
            :param addr:
            :param register:
            :return: 1 byte
            """
            pass

        def read_word(self, addr: int, register: int) -> int:
            """
            Read a single word (2 bytes) from a given register
            :param addr: i2c address
            :param register: Register to read
            :return: 2-byte word
            """
            pass

        def read_block(self, addr: int, register, length: int) -> List[int]:
            """
            Read a block of byte data from a given register
            :param addr: i2c address
            :param register: Register to read
            :param length: length in bytes
            :return: list of integer values
            """
            pass

        def write_byte_data(self, addr, register, value):
            """
            Write a byte to a given register
            :param addr: i2c address
            :param register: Register to write to
            :param value: Byte value to transmit
            """
            pass

        def write_word_data(self, addr, register, value):
            """
            Read a single word (2 bytes) from a given register
            :rtype: int
            :param addr: i2c address
            :param register: Register to read
            :return: 2-byte word
            """
            pass

        def write_block_data(self, addr, register, data):
            """
            Write a block of byte data to a given register
            :param addr: i2c address
            :param register: Start register
            :param data: List of bytes
            """
            pass

        def close(self):
            pass

    CLI_NAMESPACE = 'i2c'
    CLI_EXTENSIONS = (ListBusesCliExtension,)

    def __init__(self):
        super().__init__()
        self.__buses = {}
        self.default_bus = 1

    @staticmethod
    def typeid() -> int:
        return 0x1005

    @staticmethod
    def type_name() -> str:
        return 'I2C'

    def get_bus(self, bus_id=None) -> I2cBus:
        raise NotImplementedError()

    def list_buses(self) -> List[Tuple[str, int]]:
        raise NotImplementedError()
