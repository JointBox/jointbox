import json

import logging
from typing import List, Dict, Callable

from common.utils import int_to_hex4str
from .errors import InvalidDriverError

EVENT_STATE_CHANGED = 0x91


class InstanceSettings:
    def __init__(self):
        self.id = None
        self.context_path = []


class Driver(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def typeid() -> int:
        return -1

    @staticmethod
    def type_name() -> str:
        raise InvalidDriverError('Driver class should implement type_name() method')

    def on_initialized(self, application):
        """
        :type application: common.core.ApplicationManager
        :return:
        """
        pass

    def on_before_unloaded(self, application):
        """
        :type application: common.core.ApplicationManager
        :return:
        """
        pass


class EventDef:
    def __init__(self, id: int, name: str):
        super().__init__()
        self.id = id
        self.name = name

    def __repr__(self, *args, **kwargs):
        return 'EventDef({}, {})'.format(int_to_hex4str(self.id), self.name)


class ActionDef:
    def __init__(self, id: int, name: str, function):
        super().__init__()
        self.id = id
        self.name = name
        self.callable = function

    def __repr__(self, *args, **kwargs):
        return 'ActionDef({}, {})'.format(int_to_hex4str(self.id), self.name)


class ConfigParser(object):
    def parse(self, config_section: dict, application, absolute_path: str = ''):
        """
        :param absolute_path: String containing absolute path from the config root to the given section.
        E.g. device/test_device/acl
        :type application: common.core.ApplicationManager
        """
        raise NotImplementedError()


class ParameterDef:
    def __init__(self, name: str, is_required=False, validators=None, parser: ConfigParser = None):
        super().__init__()
        self.name = name
        self.is_required = is_required
        self.validators = validators
        self.parser = parser
        if self.validators is None:
            self.validators = []

    # def cleanup_value(self, value):
    #     return value

    def validate(self, value):
        for x in self.validators:
            if not x(value):
                raise ValueError('Parameter {} is invalid'.format(self.name))


class Serializer(object):
    def serialize(self, obj):
        raise NotImplementedError("This method needs to be implemented in child class")

    def deserialize(self, data):
        raise NotImplementedError("This method needs to be implemented in child class")


class JsonSerializer(Serializer):
    def serialize(self, obj: object):
        json.dumps(obj)

    def deserialize(self, data: str):
        return json.loads(data)


class ModelState(object):
    __DEFAULT_FILED_NAME = '$default'

    def __init__(self, fields: List[str] = None, serializer: Serializer = JsonSerializer()):
        self.fields = fields
        self.__data = {}
        self.serializer = serializer
        if self.fields is None:
            self.fields = [self.__DEFAULT_FILED_NAME]

    def read_state(self, data: str):
        self.__data = self.serializer.deserialize(data)

    def serialize_state(self):
        self.serializer.serialize(self.__data)

    def as_dict(self):
        return dict(self.__data)

    def __getattr__(self, item):
        if item == 'fields':
            return object.__getattribute__(self, item)
        if item in self.fields:
            return self.__data.get(item, None)
        else:
            return self.__getattribute__(item)

    def __setattr__(self, name, value):
        if name != 'fields':
            if name in self.fields:
                self.__data[name] = value
            else:
                return object.__setattr__(self, name, value)
        else:
            return object.__setattr__(self, name, value)


class Module:
    EVENTS = []
    ACTIONS = []  # type: List[ActionDef]
    PARAMS = []  # type: List[ParameterDef]
    REQUIRED_DRIVERS = []
    IN_LOOP = True  # Indicates that instance of of this module will be queried (step method) in main application loop
    IN_BACKGROUND = False
    MINIMAL_ITERATION_INTERVAL = 0  # Minimum interval between iterations in milliseconds

    def __init__(self, application, drivers: Dict[int, Driver]):
        """
        :type application: common.core.ApplicationManager
        """
        self.id = None
        self.name = None
        self.__application = application
        self.last_step = 0
        self.logger = logging.getLogger(self.__class__.__name__)
        self.piped_events = {}  # type: Dict[int, ]

    def get_application_manager(self):
        """
        :rtype application: ApplicationManager
        """
        return self.__application

    @staticmethod
    def typeid() -> int:
        return -1

    @staticmethod
    def type_name() -> str:
        raise InvalidDriverError('Module class should implement type_name() method')

    def emit(self, event_id, data=None):
        self.__application.emit_event(self, event_id, data)

    def step(self):
        pass

    def on_initialized(self):
        pass

    def on_before_destroyed(self):
        pass

    def validate(self):
        pass

    @classmethod
    def get_event_by_name(cls, event_name: str) -> [EventDef, None]:
        for x in cls.EVENTS:
            if x.name == event_name:
                return x
        return None

    @classmethod
    def get_action_by_name(cls, action_name: str) -> [ActionDef, None]:
        for x in cls.ACTIONS:
            if x.name == action_name:
                return x
        return None

    def __str__(self, *args, **kwargs):
        return '{}({})'.format(self.type_name(), int_to_hex4str(self.typeid()))


class StateAwareModule(Module):
    STATE_FIELDS = None

    def __init__(self, application, drivers: Dict[int, Driver]):
        super().__init__(application, drivers)
        self.EVENTS += StateAwareModule.EVENTS
        self.state = ModelState(self.STATE_FIELDS)

    def commit_state(self):
        self.emit(EVENT_STATE_CHANGED, self.state)

    EVENTS = [
        EventDef(EVENT_STATE_CHANGED, 'state_changed')
    ]


class PipedEvent(object):
    def __init__(self, declared_in: Module = None, target: Module = None, event: EventDef = None,
                 action: ActionDef = None,
                 args: dict = None):
        self.declared_in = declared_in
        self.event = event
        self.target = target
        self.args = args
        self.action = action


class InternalEvent(object):
    def __init__(self, sender: Module = None, event_id: int = None, data: dict = None):
        self.sender = sender
        self.event_id = event_id
        self.data = data


class BackgroundTask(object):
    def __init__(self, callable: Callable, *args, **kwargs):
        self.callable = callable
        self.kwargs = kwargs
        self.args = args


class ACL(object):
    MODE_RESTRICTIVE = 'restrictive'
    MODE_PERMISSIVE = 'permissive'

    SUPPORTED_MODES = [MODE_RESTRICTIVE, MODE_PERMISSIVE]

    TARGET_TYPE_ACTION = 'action'
    TARGET_TYPE_EVENT = 'event'

    SUPPORTED_TARGET_TYPES = (TARGET_TYPE_ACTION, TARGET_TYPE_EVENT)

    class Entry(object):
        def __init__(self, device_name: str = None,
                     target_type: str = None,
                     target_name: str = None):
            self.device_name = device_name
            self.__target_type = ACL.TARGET_TYPE_ACTION
            if target_type is not None:
                self.target_type = target_type
            self.target_name = target_name

        @property
        def target_type(self):
            return self.__target_type

        @target_type.setter
        def target_type(self, val):
            if val not in ACL.SUPPORTED_TARGET_TYPES:
                raise ValueError("ACL.Entry.target type should be one of: " + str(ACL.SUPPORTED_TARGET_TYPES))
            self.__target_type = val

    def __init__(self):
        super().__init__()
        self.__allowed = []
        self.__denied = []
        self.__mode = ACL.MODE_RESTRICTIVE

    @property
    def allowed(self) -> List[Entry]:
        return self.__allowed

    @property
    def denied(self) -> List[Entry]:
        return self.__denied

    @property
    def mode(self) -> str:
        return self.__mode

    @mode.setter
    def mode(self, val):
        if val not in ACL.SUPPORTED_MODES:
            raise ValueError("ACL mode should be one of: " + str(ACL.SUPPORTED_MODES))
        self.__mode = val

    def allow(self, device_name: str, target_name: str, target_type: str):
        self.__allowed.append(ACL.Entry(device_name, target_type, target_name))

    def deny(self, device_name: str, target_name: str, target_type: str):
        self.__denied.append(ACL.Entry(device_name, target_type, target_name))

    def __has_entry(self, collection:List[Entry], device_name: str, target_name: str, target_type: str):
        for entry in collection:
            if entry.device_name == device_name and entry.target_name == target_name and entry.target_type == target_type:
                return True
        return False

    def validate_operation(self, device_name: str, target_name: str, target_type: str = TARGET_TYPE_ACTION):
        if self.mode == self.MODE_RESTRICTIVE:
            if self.__has_entry(self.denied, device_name, target_name, target_type):
                return False
            return self.__has_entry(self.allowed, device_name, target_name, target_type)
        elif self.mode == self.MODE_PERMISSIVE:
            return not self.__has_entry(self.denied, device_name, target_name, target_type)
        else:
            return False