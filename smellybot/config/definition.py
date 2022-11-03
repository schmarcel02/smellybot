from typing import Dict

from smellybot.config.abstract_element import AbstractConfigElement
from smellybot.config.types import ConfigItemType
from smellybot.config.abstract_config import AbstractConfig
from smellybot.config.abstract_definition import AbstractConfigDefinition
from smellybot.config.element import ConfigElement, ListConfigElement


class ConfigDefinition(AbstractConfigDefinition):
    def __init__(self, key: str, ctype: ConfigItemType):
        super().__init__(key)
        self.key = key
        self.ctype = ctype
        self.elements: Dict[str, AbstractConfigElement] = {}

    def _create_element(self, config: AbstractConfig, location: str):
        if "." not in location:
            superior = None
        else:
            superior_location = location.rsplit(".", maxsplit=1)[0]
            superior = self.bind(config, superior_location)
        return ConfigElement(config.get_data(), self, self.key, location, self.ctype, superior)

    def bind(self, config: AbstractConfig, location: str):
        if location not in self.elements:
            self.elements[location] = self._create_element(config, location)
        return self.elements[location]

    def notify(self, location: str, operation: str, value: str):
        for sublocation, subelement in self.elements.items():
            if sublocation.startswith(location):
                subelement.notify(operation, value)


class ListConfigDefinition(ConfigDefinition):
    def __init__(self, key: str, ctype: ConfigItemType, unique: bool = False):
        super().__init__(key, ctype)
        self.unique = unique

    def _create_element(self, config: AbstractConfig, location: str) -> ListConfigElement:
        if "." not in location:
            superior = None
        else:
            superior_location = location.rsplit(".", maxsplit=1)[0]
            superior = self.bind(config, superior_location)
        return ListConfigElement(config.get_data(), self, self.key, location, self.ctype, superior, self.unique)
