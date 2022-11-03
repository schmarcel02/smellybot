from abc import ABC, abstractmethod

from smellybot.config.abstract_config import AbstractConfig
from smellybot.config.abstract_element import AbstractConfigElement


class AbstractConfigDefinition(ABC):
    def __init__(self, key: str):
        self.key = key

    @abstractmethod
    def bind(self, config: AbstractConfig, location: str) -> AbstractConfigElement:
        raise NotImplementedError()

    @abstractmethod
    def notify(self, location: str, operation: str, value: str):
        raise NotImplementedError()
