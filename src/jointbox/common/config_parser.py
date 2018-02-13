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

from jointbox.common.model import ConfigParser, ACL
from jointbox.common.parse_utils import parse_link_string


class ACLParser(ConfigParser):
    def parse(self, config_section: dict, application, absolute_path: str = '') -> ACL:
        acl = ACL()
        if 'mode' in config_section:
            acl.mode = config_section['mode']
        if 'allow' in config_section:
            for rule in config_section['allow']:
                device, action = parse_link_string(rule)
                acl.allow(device, action, ACL.TARGET_TYPE_ACTION)
        if 'deny' in config_section:
            for rule in config_section['deny']:
                device, action = parse_link_string(rule)
                acl.deny(device, action, ACL.TARGET_TYPE_ACTION)
        return acl
