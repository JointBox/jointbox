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

import json
import logging
import paho.mqtt.client as mqtt
import random
from typing import List, Tuple

from jointbox.common.drivers import DataChannelDriver, OneWireDriver, I2cDriver
from jointbox.common.drivers.gpio import GPIODriver
from jointbox.common.errors import ConfigError


class FakeGPIODriver(GPIODriver):
    def __init__(self):
        super().__init__()
        self.__logger = logging.getLogger('FakeGPIODriver')

    def new_channel(self, pin: [str, int], direction: int, pullup=True) -> GPIODriver.Channel:
        pin = self.resolve_pin_name(pin)
        if isinstance(pin, GPIODriver.Channel):
            return pin
        return GPIODriver.Channel()


class FakeWireDriver(OneWireDriver):
    DEVICES = ['28-00018370300f', '28-468003703cbf']

    def get_available_devices(self) -> List[str]:
        return self.DEVICES

    def read_temperature(self, device_name: str) -> float:
        return random.uniform(20.0, 31.0)


class FakeI2cDriver(I2cDriver):
    class I2cBus(I2cDriver.I2cBus):
        pass

    def list_buses(self) -> List[Tuple[str, int]]:
        return [('bus0', 0), ('bus1', 1)]

    def get_bus(self, bus_id=None) -> I2cBus:
        return FakeI2cDriver.I2cBus(bus_id)


class MQTTDriver(DataChannelDriver):
    class MQTTChannel(DataChannelDriver.Channel):

        class Callback:
            @staticmethod
            def create_on_connect_callback(channel):
                """
                :type channel: MQTTDriver.MQTTChannel
                :return: Callable
                """

                def cb(client, userdata, flags, rc):
                    channel.logger.info("Connected to MQTT server: Code: " + str(rc))
                    channel._connected = True
                    if not channel._was_connected:
                        channel._was_connected = True
                        try:
                            channel.on_connect_first_time(client)
                        except Exception as e:
                            channel.logger.error("Error while running on_connect_first_time callback: " + str(e))
                    try:
                        channel.on_connect(client)
                    except Exception as e:
                        channel.logger.error("Error while running on_connect callback: " + str(e))

                return cb

            @staticmethod
            def create_on_disconnect_callback(channel):
                """
                :type channel: MQTTDriver.MQTTChannel
                :return: Callable
                """

                def cb(client, userdata, rc):
                    channel.logger.info("Disconnected from MQTT server: Code: " + str(rc))
                    channel._connected = False

                return cb

            # The callback for when a PUBLISH message is received from the server.
            @staticmethod
            def create_on_message_callback(channel):
                """
                :type channel: MQTTDriver.MQTTChannel
                :return: Callable
                """

                def cb(client, userdata, msg):
                    try:
                        channel.on_data_received(msg)
                    except Exception as e:
                        channel.logger.error(
                            'Unable to handle message: ' + msg.topic + ", msg: " + str(msg.payload) + ', error: ' + str(
                                e))

                return cb

        def __init__(self, driver, connection_options: dict):
            """
            :type driver: MQTTDriver
            """
            super().__init__(connection_options)
            self.logger = driver.logger
            self._connected = False
            self._was_connected = False
            self._thread = None
            try:
                self.bind_address = connection_options.get('bind_address', '0.0.0.0')
                self.server_address = connection_options.get('server_address', '127.0.0.1')
                self.server_port = connection_options.get('port', 1883)
                self.topic_prefix = connection_options.get('topic_prefix', 'rmod')
            except KeyError as e:
                raise ConfigError("Unable to build MQTT communication channel because of configuration error: "
                                  + str(e))
            self._mqtt_client = mqtt.Client()
            self._mqtt_client.on_connect = self.Callback.create_on_connect_callback(self)
            self._mqtt_client.on_disconnect = self.Callback.create_on_disconnect_callback(self)
            self._mqtt_client.on_message = self.Callback.create_on_message_callback(self)

        def __encode_value(self, value):
            if isinstance(value, dict):
                return json.dumps(value)
            else:
                return str(value)

        def send(self, destination: str, data):
            raw_data = None
            if isinstance(data, dict):
                raw_data = data
            else:
                raise ValueError("MQTTChannel supports only dictionary data")
            for key, value in raw_data.items():
                try:
                    result, msg_id = self._mqtt_client.publish('{}{}/{}'.format(self.topic_prefix, destination, key),
                                                               self.__encode_value(value))
                except Exception as e:
                    self.logger.error("Unable to send MQTT message: " + str(e))

        def is_connected(self) -> bool:
            return self._connected

        def connect(self):
            if not self._was_connected:
                self._mqtt_client.connect_async(self.server_address, port=self.server_port,
                                                bind_address=self.bind_address)
            self._mqtt_client.reconnect()

        def step(self):
            try:
                self._mqtt_client.loop()
            except Exception as e:
                pass

        def disconnect(self):
            self._mqtt_client.disconnect()

    def __init__(self):
        super().__init__()
        self.__thread_manager = None  # type: common.core.ThreadManager
        self.__channel_counter = 0

    def on_initialized(self, application):
        """
        :type application: common.core.ApplicationManager
        :return:
        """
        self.__thread_manager = application.thread_manager

    def new_channel(self, connection_options: dict) -> MQTTChannel:
        def do_step(channel):
            channel.step()

        channel = MQTTDriver.MQTTChannel(self, connection_options)
        self.__channel_counter += 1
        thread = self.__thread_manager.request_thread('MQTTDriver-ch' + str(self.__channel_counter), channel.step, [])
        channel.dispose = lambda: self.__thread_manager.dispose_thread(thread)
        return channel
