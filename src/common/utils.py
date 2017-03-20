import time


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