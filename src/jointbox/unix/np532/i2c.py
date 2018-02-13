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

"""@package py532lib.i2c
This module contains classes and functions related to I2C communication for the PN532 NFC Chip.

@author:  DanyO <me@danyo.ca>
@license: The source code within this file is licensed under the BSD 2 Clause license.
          See LICENSE file for more information.

"""
from time import sleep
import logging

from jointbox.common.drivers import I2cDriver
from .frame import *
from .constants import *

DEFAULT_DELAY = 0.01


class Pn532I2c:
    """Pn532_i2c abstracts away the details related to
    I2C communication with the PN532.

    """

    def __init__(self, i2c_driver: I2cDriver, i2c_address=PN532_I2C_SLAVE_ADDRESS, i2c_channel=1):
        """Constructor for the Pn532_i2c class.

        Arguments:
        @param[in]  address     I2C slave address for the PN532
                                (default = PN532_FRAME_TYPE_DATA)

        @param[in]  i2c_channel I2C channel to use.
                                (default = RPI_DEFAULT_I2C_NEW)

        """
        self.logger = logging.getLogger("Pn532_i2c")
        self.address = i2c_address
        self.i2c_channel = i2c_channel
        self._driver = i2c_driver
        self._bus = self._driver.get_bus(i2c_channel)

    def send_command_check_ack(self, frame):
        """Sends a command frame, and waits for an ACK frame.

        Arguments:
        @param[in]  frame   Pn532Frame to send.

        """
        logging.debug("send_command_check_ack")
        self.send_command(frame)
        if self.read_ack():
            return True
        else:
            return False

    def read_response(self):
        """Wait, then read for a response from the PN532."""
        logging.debug("readResponse...")
        response = [b'\x00\x00\x00\x00\x00\x00\x00']

        while True:

            try:
                logging.debug("readResponse..............Reading.")

                sleep(1)
                #response = []
                logging.debug("  2 bytes:" + str(self._bus.read_word(self.address, 0)))
                response = self._bus.read_block(self.address, 0, 32)
                logging.debug("response: " + str(response))
                logging.debug("readResponse..............Read.")
            except Exception:
                logging.exception("read err")
            else:
                try:
                    frame = Pn532Frame.from_response(response)

                    # Acknowledge Data frames coming from the PN532
                    if frame.get_frame_type() == PN532_FRAME_TYPE_DATA:
                        self.send_command(Pn532Frame(
                            frame_type=PN532_FRAME_TYPE_ACK))

                except Exception as ex:
                    logging.debug(ex)
                    logging.debug(ex.args)
                    pass
                else:
                    return frame

    def send_command(self, frame):
        """Sends a command frame to the PN532.

        Arguments:
        @param[in]  frame   Pn532Frame to send.

        """
        logging.debug("send_command...")

        while True:
            try:
                logging.debug("send_command...........Sending.")
                data = frame.to_tuple()
                #data = [1,2,3,4,5,6,7]
                #data = [0, 0, 255, 5, 251, 212, 20, 1, 1, 5, 22, 0]
                logging.debug("  Data: " + str(data))
                sleep(DEFAULT_DELAY)
                self._bus.write_block_data(self.address, 0, data)

                logging.debug("send_command...........Sent.")
            except Exception as ex:
                logging.exception(str(ex))

                self.reset_i2c()
                sleep(DEFAULT_DELAY)
            else:
                return True

    def read_ack(self):
        """Wait for a valid ACK frame to be returned."""
        logging.debug("read_ack...")

        while True:
            sleep(DEFAULT_DELAY)
            response_frame = self.read_response()

            if response_frame.get_frame_type() == PN532_FRAME_TYPE_ACK:
                return True
            else:
                pass

    def read_mifare(self):
        """Wait for a MiFARE card to be in the PN532's field, and read it's UID."""
        frame = Pn532Frame(frame_type=PN532_FRAME_TYPE_DATA,
                           data=bytearray([PN532_COMMAND_INLISTPASSIVETARGET, 0x01, 0x00]))
        self.send_command_check_ack(frame)

        return self.read_response()

    def reset_i2c(self):
        """Reset the I2C communication connection."""
        logging.debug("I2C Reset...")

        # self._bus.close()
        # del self._bus
        # self._bus = self._driver.get_bus(self.i2c_channel)

        logging.debug("I2C Reset............Created.")

    def SAMconfigure(self, frame=None):
        """Send a SAMCONFIGURATION command to the PN532.

        Arguments:
        @param[in]  frame   Custom SAMconfigure options can be passed here.

        """
        logging.debug("SAMconfigure")
        if frame is None:
            frame = Pn532Frame(frame_type=PN532_FRAME_TYPE_DATA,
                               data=bytearray(
                                   [PN532_COMMAND_SAMCONFIGURATION,
                                    PN532_SAMCONFIGURATION_MODE_NORMAL,
                                    PN532_SAMCONFIGURATION_TIMEOUT_50MS,
                                    PN532_SAMCONFIGURATION_IRQ_OFF]))

        self.send_command_check_ack(frame)

    def close(self):
        if self._bus:
            self._bus.close()
            del self._bus

    def __exit__(self, type, value, traceback):
        """Make sure the I2C communication channel is closed."""
        self.close()
