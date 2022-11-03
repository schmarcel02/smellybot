from abc import ABC, abstractmethod
from typing import Any, Optional, Callable


class AbstractConfigElement(ABC):
    @abstractmethod
    def get(self):
        raise NotImplementedError()

    @abstractmethod
    def set(self, value: Any):
        raise NotImplementedError()

    @abstractmethod
    def key_set(self, key: str, value: Any):
        raise NotImplementedError()

    @abstractmethod
    def add(self, value: Any):
        raise NotImplementedError()

    @abstractmethod
    def remove(self, value: Any):
        raise NotImplementedError()

    @abstractmethod
    def notify(self, operation: str, value: Optional[Any]):
        raise NotImplementedError()

    @abstractmethod
    def add_listener(self, operation: Optional[str], listener: Callable[[str, Any], None]):
        raise NotImplementedError()