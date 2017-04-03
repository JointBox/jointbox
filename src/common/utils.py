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