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

"""@package py532lib.constants
This module contains the constants related to py532lib.

@author:  DanyO <me@danyo.ca>
@license: The source code within this file is licensed under the BSD 2 Clause license.
          See LICENSE file for more information.

"""
# Typical PN532 slave address on RPi.
PN532_I2C_SLAVE_ADDRESS = 0x24

# PN532 Commands
PN532_COMMAND_GETFIRMWAREVERSION = 0x02
PN532_COMMAND_SAMCONFIGURATION = 0x14
PN532_COMMAND_INLISTPASSIVETARGET = 0x4A
PN532_COMMAND_RFCONFIGURATION = 0x32
PN532_COMMAND_INDATAEXCHANGE = 0x40
PN532_COMMAND_INDESELECT = 0x44

# Frame Identifiers
PN532_IDENTIFIER_HOST_TO_PN532 = 0xD4
PN532_IDENTIFIER_PN532_TO_HOST = 0xD5

# Values for PN532's SAMCONFIGURATION function.
PN532_SAMCONFIGURATION_MODE_NORMAL = 0x01
PN532_SAMCONFIGURATION_MODE_VIRTUAL_CARD = 0x02
PN532_SAMCONFIGURATION_MODE_WIRED_CARD = 0x03
PN532_SAMCONFIGURATION_MODE_DUAL_CARD = 0X04

PN532_SAMCONFIGURATION_TIMEOUT_50MS = 0x01

PN532_SAMCONFIGURATION_IRQ_OFF = 0x00
PN532_SAMCONFIGURATION_IRQ_ON = 0x01

# Values for the PN532's RFCONFIGURATION function.
PN532_RFCONFIGURATION_CFGITEM_MAXRETRIES = 0x05

# Typical frame values.
PN532_PREAMBLE = 0x00
PN532_START_CODE_1 = 0x00
PN532_START_CODE_2 = 0xFF
PN532_POSTAMBLE = 0x00

# Position of info within the communication's frame.
PN532_FRAME_POSITION_STATUS_CODE = 0
PN532_FRAME_POSITION_PREAMBLE = 1
PN532_FRAME_POSITION_START_CODE_1 = 2
PN532_FRAME_POSITION_START_CODE_2 = 3
PN532_FRAME_POSITION_LENGTH = 4
PN532_FRAME_POSITION_LENGTH_CHECKSUM = 5
PN532_FRAME_POSITION_FRAME_IDENTIFIER = 6
PN532_FRAME_POSITION_DATA_START = 7

# Type of frame.
PN532_FRAME_TYPE_DATA = 0
PN532_FRAME_TYPE_ACK = 1
PN532_FRAME_TYPE_NACK = 2
PN532_FRAME_TYPE_ERROR = 3