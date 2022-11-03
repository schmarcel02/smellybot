from abc import ABC, abstractmethod

from smellybot.config.abstract_data import AbstractConfigData


class AbstractConfig(ABC):
    @abstractmethod
    def get_data(self) -> AbstractConfigData:
        raise NotImplementedError()
