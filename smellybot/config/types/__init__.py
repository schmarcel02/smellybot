from abc import ABC, abstractmethod
from typing import Any

from smellybot.config.exceptions import ConfigException


class ConfigParseError(ConfigException):
    pass


class ConfigItemType(ABC):
    @abstractmethod
    def parse(self, value: Any) -> Any:
        raise NotImplementedError()

    def to_store_format(self, value: Any) -> Any:
        return value

    def from_store_format(self, value: Any) -> Any:
        return value
