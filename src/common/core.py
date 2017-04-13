import logging
import threading

import time
from queue import Queue
from threading import Thread

from typing import Dict, Callable, List, Any
from typing import Tuple

from common import utils
from common.model import CliExtension, CliExtensionsAwareComponent
from .utils import int_to_hex4str
from .errors import InvalidModuleError, InvalidDriverError, LifecycleError
from .model import InstanceSettings, Driver, DeviceModule, InternalEvent, PipedEvent, BackgroundTask, ActionDef, Module


def _register_cli_extensions(application, source_class: CliExtensionsAwareComponent):
    """
    :type application: ApplicationManager
    """
    if application.get_instance_settings().enable_cli:
        for extension in source_class.CLI_EXTENSIONS:
            namespace = source_class.CLI_NAMESPACE if source_class.CLI_NAMESPACE is not None \
                else source_class.type_name()
            application.cli_extensions.append((namespace, extension))


class ModuleRegistry:
    def __init__(self, application_manager):
        super().__init__()
        self.modules = {}  # type: Dict[DeviceModule]
        self.__application = application_manager  # type: ApplicationManager

    def find_module_by_name(self, module_name):
        for x in self.modules.values():
            if x.type_name() == module_name:
                return x
        raise InvalidModuleError('Unknown module {} '.format(module_name))

    def register(self, module_class):
        module_class_name = module_class.__name__
        try:
            # Validations
            if not issubclass(module_class, Module):
                raise InvalidModuleError("DeviceModule should implement DeviceModule class")
            typeid = module_class.typeid()
            if typeid < 0:
                raise InvalidModuleError('Incorrect module type')
            if typeid in self.modules.keys():
                raise InvalidModuleError(
                    'DeviceModule {} is already registered'.format(int_to_hex4str(typeid), module_class.type_name()))
            # Process CLI Extensions if needed
            _register_cli_extensions(self.__application, module_class)
            self.modules[typeid] = module_class
        except InvalidModuleError as e:
            raise InvalidModuleError("Can't register module " + module_class_name + ": " + e.message, e)

    def create_module_instance(self, application, typeid: int, instance_id: int, instance_name: str) -> DeviceModule:
        """
        :type application: ApplicationManager
        :return:
        """
        try:
            if typeid not in self.modules:
                raise InvalidModuleError("Unknown module type:".format(typeid))
            cls = self.modules.get(typeid)  # type: class[Module]
            if not issubclass(cls, DeviceModule):
                raise InvalidModuleError("DeviceModule should implement DeviceModule class")
            # Resolve required drivers
            drivers = {}
            if cls.REQUIRED_DRIVERS is not None:
                for driver_type_id_or_name in cls.REQUIRED_DRIVERS:
                    if isinstance(driver_type_id_or_name, int):
                        driver = application.get_driver(driver_type_id_or_name)
                        if driver is None:
                            raise InvalidModuleError("DeviceModule {} requires driver {} which is not available"
                                                     .format(cls, driver_type_id_or_name))
                        drivers[driver.typeid()] = driver
                    else:
                        raise InvalidModuleError("DeviceModule " + str(cls) + ' is invalid. REQUIRED_DRIVERS should '
                                                                              'contain the list of driver IDs')
            instance = cls(application, drivers)
            instance.id = instance_id
            instance.name = instance_name
            # Parameters and validation
            # TODO:
            return instance
        except InvalidModuleError as e:
            raise InvalidModuleError("Unable to create module for device {}: {}".format(instance_id, e.message), e)


class ThreadManager(object):
    DEFAULT_THREAD_INTERVAL = 200

    def __init__(self):
        self.__managed_threads = {}
        self.logger = logging.getLevelName(self.__class__.__name__)

    def request_thread(self, name, callback, context: [List, None] = None,
                       step_interval=DEFAULT_THREAD_INTERVAL) -> Thread:
        thread_name = 'm-' + str(name)
        if context is None:
            context = ()

        def on_step():
            while not threading.currentThread().terminating:
                try:
                    callback(*context)
                    time.sleep(float(step_interval) / 1000)
                except Exception as e:
                    self.logger.error('Thread execution failed: {}'.format(e))

        thread = Thread(target=on_step, name=thread_name)
        thread.terminating = False
        self.__managed_threads[thread_name] = thread
        thread.start()
        return thread

    def dispose_thread(self, thread: [Thread, str]):
        thread_name = thread.getName()
        # if isinstance(thread, Thread):
        #     thread_name = thread.getName()
        # else:
        #     thread_name = thread
        #     thread = self.__managed_threads.get(thread_name)
        if thread_name in self.__managed_threads.keys():
            thread.terminating = True
            self.__managed_threads.pop(thread_name)
        else:
            raise LifecycleError("Can't dispose thread {} because it is not managed thread".format(thread_name))

    def dispose_all(self):
        threads = list(self.__managed_threads.values())
        for t in threads:
            self.dispose_thread(t)


class ApplicationManager:
    EVENT_HANDLING_LOOP_INTERVAL = 50
    BG_TASK_HANDLING_LOOP_INTERVAL = 50
    MAIN_LOOP_INTERVAL = 50

    def __init__(self):
        self.__instance_settings = InstanceSettings()
        self.drivers = {}  # type: Dict[int, Driver]
        self.devices = {}  # type: Dict[int, DeviceModule]
        self.cli_extensions = []  # type: List[Tuple[str, CliExtension]]
        self.thread_manager = ThreadManager()
        self.__logger = logging.getLogger('ApplicationManager')
        self.__main_loop = []
        self.__module_registry = ModuleRegistry(self)
        self.__terminating = False
        self.__event_queue = Queue()
        self.__bg_tasks_queue = Queue()
        self.__event_map = {}  # type: Dict[int, List[PipedEvent]]

    def get_instance_settings(self) -> InstanceSettings:
        return self.__instance_settings

    def get_module_registry(self) -> ModuleRegistry:
        return self.__module_registry

    def get_driver_by_name(self, name: str) -> Driver:
        raise NotImplementedError()

    def get_device_by_name(self, name: str) -> [DeviceModule, None]:
        for x in self.devices.values():
            if x.name == name:
                return x
        return None

    def get_driver(self, driver_type: int) -> Driver:
        driver_impl = self.drivers.get(driver_type, None)  # type: Driver
        if driver_impl is None:
            raise InvalidDriverError(
                'There is no implementation for driver {} registered'.format(int_to_hex4str(driver_type)))
        return driver_impl

    def register_driver(self, driver_class_name):
        try:
            if isinstance(driver_class_name, str):
                # Load driver
                try:
                    module_name, class_name = driver_class_name.rsplit('.', 1)
                    module = __import__(module_name, globals(), locals(), [class_name], 0)
                    driver_impl_class = getattr(module, class_name)
                except ImportError as e:
                    raise InvalidDriverError("Class doesn't exist", e)
            else:
                driver_impl_class = driver_class_name
            # Validations
            if not issubclass(driver_impl_class, Driver):
                raise InvalidDriverError('Driver should implement common.model.Driver class')
            typeid = driver_impl_class.typeid()
            if typeid < 0:
                raise InvalidDriverError('Incorrect driver type')
            if typeid in self.drivers.keys():
                raise InvalidDriverError(
                    'Driver implementation for {} is already registered'.format(driver_impl_class.type_name()))
            # Process CLI Extensions if needed
            _register_cli_extensions(self, driver_impl_class)
            # Initialization
            driver_impl = driver_impl_class()
            try:
                driver_impl.on_initialized(self)
            except Exception as e:
                raise InvalidDriverError("Error during initialization", e)
            self.drivers[typeid] = driver_impl
            self.__logger.info('Loaded driver {}({} driver): '.format(int_to_hex4str(driver_impl.typeid()),
                                                                      driver_impl.type_name()) + driver_impl.__class__.__name__)
        except InvalidDriverError as e:
            raise InvalidDriverError('Unable to register driver {}: '.format(driver_class_name) + e.message, e)

    def register_device(self, device: DeviceModule):
        self.devices[device.id] = device
        if device.IN_LOOP:
            self.__main_loop.append(device)

    def register_pipe(self, piped_event: PipedEvent):
        event_list = self.__event_map.get(piped_event.event.id, None)
        if event_list is None:
            event_list = []
            self.__event_map[piped_event.event.id] = event_list
        event_list.append(piped_event)

    def run_async_action(self, device: DeviceModule, action: ActionDef, data=None, sender=None):
        self.__bg_tasks_queue.put(BackgroundTask(action.callable, device, data, **dict(sender=sender)))

    def emit_event(self, sender: DeviceModule, event_id: int, data: dict = None):
        self.__event_queue.put(InternalEvent(sender, event_id, data))

    def run_async(self, callable, ignore_errors=False, *args, **kwargs):
        self.__bg_tasks_queue.put(BackgroundTask(callable, ignore_errors=ignore_errors, *args, **kwargs))

    def main_loop(self):
        while not self.__terminating:

            for device in self.__main_loop:
                if device.last_step > 0 and utils.delta_time(device.last_step) < device.MINIMAL_ITERATION_INTERVAL:
                    continue
                try:
                    start_time = utils.capture_time()
                    if device.IN_BACKGROUND:
                        self.run_async(device.step)
                    else:
                        device.step()
                    delta = utils.capture_time() - start_time
                    if delta > 100:
                        self.__logger.warning(
                            "Device {} might cause performance issues. It has occupied main thread for {}ms".format(
                                device.name, delta))
                except Exception as e:
                    self.__logger.error("Error in during main loop execution: " + str(e))
                finally:
                    # TODO: For BG task we should update time after actual execution
                    device.last_step = utils.capture_time()
            time.sleep(0.001)

    def event_loop(self):
        while not self.__terminating and not self.__event_queue.empty():
            try:
                event_task = self.__event_queue.get()  # type: InternalEvent
                pipes = self.__event_map.get(event_task.event_id, [])
                for pipe in pipes:
                    try:
                        pipe.action.callable(pipe.target, event_task.data,
                                             **dict(event=pipe.event, sender=event_task.sender))
                    except Exception as e:
                        self.__logger.error("Unhandled error in ${}.{}: {}".format(pipe.target, pipe.action.name, e))
            except Exception as e:
                self.__logger.error("Error in during event loop execution: " + str(e))

    def background_tasks_loop(self):
        while not self.__terminating and not self.__bg_tasks_queue.empty():
            task = self.__bg_tasks_queue.get()  # type: BackgroundTask
            try:
                c = task.callable
                c(*task.args, **task.kwargs)
            except Exception as e:
                if not task.ignore_errors:
                    self.__logger.error("Unhandled error during background task execution: {}".format(e))

    def shutdown(self):
        self.__logger.info("Initiating shutdown process")
        self.__terminating = True
        for device in self.devices.values():
            try:
                device.on_before_destroyed()
            except Exception as e:
                self.__logger.error(
                    "Error while destroying device {}({}): {}".format(int_to_hex4str(device.id), device.name, e))
        self.__logger.info("Deactivated devices")
        for driver in self.drivers.values():
            try:
                driver.on_before_unloaded(self)
            except Exception as e:
                self.__logger.error(
                    "Error while destroying driver {}({}): {}".format(int_to_hex4str(driver.typeid()),
                                                                      driver.type_name(), e))
        self.__logger.info("Unloaded drivers")
        self.thread_manager.dispose_all()
        self.__logger.info("Disposed supplementary threads")
