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
