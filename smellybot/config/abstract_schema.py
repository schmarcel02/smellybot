from abc import ABC, abstractmethod

from smellybot.config.abstract_definition import AbstractConfigDefinition


class AbstractConfigSchema(ABC):
    @abstractmethod
    def register(self, definition: AbstractConfigDefinition):
        raise NotImplementedError()

    @abstractmethod
    def get_definition(self, key: str) -> AbstractConfigDefinition:
        raise NotImplementedError()
