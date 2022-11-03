from typing import Optional, Dict, cast

from smellybot.access_control import Everyone, AccessControl, ModPlus
from smellybot.context import MessageContext
from smellybot.config.abstract_config import AbstractConfig
from smellybot.config.abstract_data import AbstractConfigData
from smellybot.config.abstract_definition import AbstractConfigDefinition
from smellybot.config.abstract_element import AbstractConfigElement
from smellybot.config.abstract_schema import AbstractConfigSchema
from smellybot.config.exceptions import DuplicateConfigException, ConfigNotFoundException
from smellybot.config.secure_definition import SecureConfigDefinition


class Config(AbstractConfig):
    def __init__(self, name: str, parent: Optional['Config'] = None, channel_restriction: str = None,
                 access_control: AccessControl = ModPlus()):
        self.name = name
        self.id: str = parent.id + "." + name if parent else name
        self.root = parent.root if parent else self
        self.parent = parent
        self.schema: AbstractConfigSchema = (parent or self).schema
        self.data: AbstractConfigData = (parent or self).data
        self.children: Dict[str, Config] = {}

        self.channel_restriction = channel_restriction
        self.access_control = access_control

        if parent:
            parent.add_child(self)

    def get_data(self) -> AbstractConfigData:
        return self.data

    def load(self):
        self.data.load()

    def save(self):
        self.data.save()

    def add_child(self, child: 'Config'):
        if child.name in self.children:
            raise DuplicateConfigException(child.name)
        self.children[child.name] = child

    def has_child(self, name: str):
        return name in self.children

    def remove_child(self, name: str):
        del self.children[name]

    def get_child(self, name: str) -> 'Config':
        child = self.children.get(name)
        if child:
            return child
        raise ConfigNotFoundException()

    def check(self, context: MessageContext):
        return (self.channel_restriction is None or context.channel.name.lower() == self.channel_restriction.lower()) \
               and self.access_control.check(context.author)

    def get_definition(self, key: str) -> SecureConfigDefinition:
        return cast(SecureConfigDefinition, self.schema.get_definition(key))

    def register(self, config_definition: AbstractConfigDefinition,
                 read_access_control: AccessControl = ModPlus(), write_access_control: AccessControl = None) -> AbstractConfigElement:
        definition = self.schema.register(
            SecureConfigDefinition(config_definition, read_access_control, write_access_control)
        )
        return definition.bind(self, self.id)

    def element(self, key: str) -> AbstractConfigElement:
        definition = self.schema.get_definition(key)
        return definition.bind(self, self.id)


class ConfigRoot(Config):
    def __init__(self, schema: AbstractConfigSchema, data: AbstractConfigData, channel_restriction: str = None,
                 access_control: AccessControl = Everyone):
        self.schema = schema
        self.data = data
        super().__init__("", None, channel_restriction, access_control)
