from abc import ABC, abstractmethod
from typing import Any


class AbstractConfigData(ABC):
    @abstractmethod
    def load(self):
        raise NotImplementedError()

    @abstractmethod
    def save(self):
        raise NotImplementedError()

    @abstractmethod
    def get(self, location: str, key: str):
        raise NotImplementedError()

    @abstractmethod
    def set(self, key: str, location: str, value: Any):
        raise NotImplementedError()
