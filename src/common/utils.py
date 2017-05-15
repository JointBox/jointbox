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

import time

import sys
import traceback


def int_to_hex4str(val: int) -> str:
    return hex(val)


def capture_time() -> int:
    """
    :return: Time in milliseconds
    """
    return int(time.time() * 1000)  # Fractional seconds to millis


def delta_time(point_in_time: int, now: int = None) -> int:
    """
    :param point_in_time: time in milliseconds
    :param now: current time in milliseconds
    :return: difference in milliseconds
    """
    if now is None:
        now = capture_time()
    return now - point_in_time


def busy_wait(time_in_millis):
    """    
    :param time_in_millis: time delta in milliseconds 
    :return: 
    """
    start = capture_time()
    while delta_time(start) < time_in_millis:
        pass


class CLI:
    verbose_mode = False

    @classmethod
    def print_data(cls, msg: str):
        print(msg)

    @classmethod
    def print_info(cls, msg: str):
        print(msg, file=sys.stderr)

    @classmethod
    def print_error(cls, exception):
        print(" -> ERROR: " + str(exception), file=sys.stderr)
        if cls.verbose_mode:
            print('--------------')
            traceback.print_exc(file=sys.stderr)

    @classmethod
    def print_debug(cls, string_to_print):
        if cls.verbose_mode:
            print('[DEBUG] ' + string_to_print, file=sys.stderr)
