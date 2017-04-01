from typing import Dict

from common.config_parser import ACLParser
from common.drivers import DataChannelDriver
from common.errors import RPCError
from common.model import DeviceModule, ParameterDef, ActionDef, Driver, EventDef, ModelState, ACL
from common import validators

ACTION_PUSH = 0x01
ACTION_PUSH_STATE = 0x02


class CommunicationBusModule(DeviceModule):
    TOPIC_PREFIX = 'rmod'
    TOPIC_STATE_SUFFIX = '/state'
    TOPIC_ACTION_SUFFIX = '/action'
    TOPIC_CMD_SUFFIX = '/_cmd'
    DEFAULT_BROKER_PORT = 2131

    @staticmethod
    def typeid() -> int:
        return 0x0110

    @staticmethod
    def type_name() -> str:
        return 'CommunicationBus'

    def __on_connect_first_time(self, client):
        try:
            client.subscribe("{}/#".format(self._rpc_topic_prefix))
        except Exception as e:
            self.logger.error("Unable to subscribe for command interface: " + str(e))
            self.logger.warn("Remote action call will be disabled" + str(e))

    def __on_message_received(self, msg):
        if msg.topic.startswith(self._rpc_topic_prefix):
            payload_str = str(msg.payload, 'utf-8')
            self.logger.debug(
                'Got new message: topic: {}, payload: {}'.format(msg.topic, payload_str))
            device_name, action_name = msg.topic[len(self._rpc_topic_prefix) + 1:].split('/', 1)
            device = self.get_application_manager().get_device_by_name(device_name)
            if device is None:
                raise RPCError("Unknown device {}.".format(device_name), cmd=msg)
            action_def = device.get_action_by_name(action_name)
            if action_def is None:
                raise RPCError("Unknown action #{}.{}.".format(device_name, action_name), cmd=msg)
            if not self.acl.validate_operation(device_name, action_name):
                raise RPCError("Access denied for RPC call #{}.{}".format(device_name, action_name))
            self.get_application_manager().run_async_action(device, action_def, payload_str, self)

    def __init__(self, application, drivers: Dict[int, Driver]):
        """
        :type application: common.core.ApplicationManager
        """
        super().__init__(application, drivers)
        self.server_address = ''
        self.server_port = self.DEFAULT_BROKER_PORT
        self.bind_address = ''
        self.topic_name = CommunicationBusModule.TOPIC_PREFIX + (
            application.get_instance_settings().id if application.get_instance_settings().id is not None else ''
        )
        self._channel_driver = drivers.get(DataChannelDriver.typeid())  # type: DataChannelDriver
        self.channel = None  # type: DataChannelDriver.Channel
        self.acl = ACL()
        self._rpc_topic_prefix = self.TOPIC_PREFIX + self.TOPIC_CMD_SUFFIX

    def push(self, data=None, **kwargs):
        if self.channel.is_connected():
            self.channel.send('TODO', data)

    def push_state(self, data: ModelState = None, event: EventDef = None, sender: DeviceModule = None, **kwargs):
        if not self.channel.is_connected():
            return  # We can't sync message until establish connection
        try:
            assert isinstance(data, ModelState), "push_state action expects StateModel, got " + str(data)
            self.channel.send('/{}/state'.format(sender.name), data.as_dict())
        except Exception as e:
            self.logger.error("Unable to push device state: " + str(e))

    def on_initialized(self):
        self.channel = self._channel_driver.new_channel({
            "server_address": self.server_address,
            "server_port": self.server_port,
            "bind_address": self.bind_address,
            "topic_prefix": self.topic_name
        })
        self.channel.on_data_received = self.__on_message_received
        self.channel.on_connect_first_time = self.__on_connect_first_time

    def step(self):
        # We just need to check if connection is alive. If not - reconnect
        if not self.channel.is_connected():
            try:
                self.channel.connect()
            except Exception as e:
                pass  # We will try to reconnect a bit later

    def on_before_destroyed(self):
        self.channel.disconnect()
        self.channel.dispose()

    ACTIONS = [
        ActionDef(ACTION_PUSH, 'push', push),
        ActionDef(ACTION_PUSH_STATE, 'push_state', push_state)
    ]

    PARAMS = [
        ParameterDef(name='server_address', is_required=True),
        ParameterDef(name='server_port', is_required=False, validators=[validators.integer]),
        ParameterDef(name='bind_address', is_required=False),
        ParameterDef(name='acl', is_required=False, parser=ACLParser())
    ]
    IN_LOOP = True
    REQUIRED_DRIVERS = [DataChannelDriver.typeid()]
    MINIMAL_ITERATION_INTERVAL = 5 * 1000
