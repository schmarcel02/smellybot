from smellybot.access_control import AccessControl
from smellybot.config.abstract_config import AbstractConfig
from smellybot.config.abstract_definition import AbstractConfigDefinition
from smellybot.context import MessageContext


class SecureConfigDefinition(AbstractConfigDefinition):
    def __init__(self, wrapped: AbstractConfigDefinition,
                 read_access_control: AccessControl, write_access_control: AccessControl = None):
        super().__init__(wrapped.key)
        self._wrapped = wrapped
        self.read_access_control = read_access_control
        self.write_access_control = write_access_control or read_access_control

    def check_read(self, context: MessageContext):
        return self.read_access_control.check(context.author)

    def check_write(self, context: MessageContext):
        return self.write_access_control.check(context.author)

    def bind(self, config: AbstractConfig, location: str):
        return self._wrapped.bind(config, location)

    def notify(self, location: str, operation: str, value: str):
        self._wrapped.notify(location, operation, value)
