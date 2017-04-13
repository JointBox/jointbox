import logging

from typing import Dict

from common.model import DeviceModule, Driver, ActionDef, EventDef

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
