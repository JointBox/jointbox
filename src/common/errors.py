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

class SimpleException(Exception):
    def __init__(self, message, ex=None):
        self.message = message
        self.ex = ex


class ConfigValidationError(SimpleException):
    def __init__(self, section_name, message, ex=None):
        super().__init__(message, ex)
        self.section = section_name

    def __repr__(self, *args, **kwargs):
        return "Invalid configuration: [" + self.section + ']: ' + self.message


class ConfigError(SimpleException):
    pass


class InvalidDriverError(SimpleException):
    pass


class InvalidModuleError(SimpleException):
    pass


class LifecycleError(SimpleException):
    pass


class RPCError(SimpleException):
    def __init__(self, message, ex=None, cmd=None):
        super().__init__(message, ex)
        self.cmd = cmd

    def __repr__(self, *args, **kwargs):
        return "Invalid remote command: " + self.message
