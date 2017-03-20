from common.model import ConfigParser, ACL
from common.parse_utils import parse_link_string


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
