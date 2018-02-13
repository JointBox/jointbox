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

import logging

from typing import Dict

from jointbox.common.model import DeviceModule, Driver, ActionDef, EventDef

ACTION_LOG = 0x010101


class LoggerModule(DeviceModule):
    def __init__(self, application, drivers: Dict[int, Driver]):
        super().__init__(application, drivers)
        self.__logger = None

    def on_initialized(self):
        self.__logger = logging.getLogger('L-' + self.name)
        self.__logger.info('Logging device initialized')

    def log(self, data=None, **kwargs):
        self.__logger.info('data={}, context={}'.format(data, kwargs))

    @staticmethod
    def type_name() -> str:
        return 'Logger'

    @staticmethod
    def typeid() -> int:
        return 0x0101

    ACTIONS = [
        ActionDef(ACTION_LOG, 'log', log),
    ]
