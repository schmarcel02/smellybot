from smellybot.chat_exception import ChatException


class ConfigException(ChatException):
    pass


class ConfigParseException(ConfigException):
    pass


class DuplicateConfigException(ConfigException):
    pass


class ConfigNotFoundException(ConfigException):
    pass


class ConfigNotSetException(ConfigException):
    pass


class ProtectedConfigException(ConfigException):
    pass


class SetListException(ConfigException):
    pass


class AddToNonListException(ConfigException):
    pass


class OperationNotSupportedException(ConfigException):
    pass
