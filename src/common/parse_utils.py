from typing import Tuple

from common.errors import ConfigError


def parse_link_string(link_string: str) -> Tuple[str, str]:
    """
    Returns tuple: (device_id, action). If action is not set - returns (device_id, None)
    """
    if '.' in link_string:
        device_id, action = link_string.split('.')
    else:
        device_id, action = link_string, None
    if device_id.startswith('#'):
        device_id = device_id.replace('#', '')
    else:
        raise ConfigError('Invalid link: ' + link_string)
    return device_id, action
