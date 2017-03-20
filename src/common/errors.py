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
