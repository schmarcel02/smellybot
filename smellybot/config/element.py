from typing import Any, List, Optional, Callable, Tuple

from smellybot.config.abstract_data import AbstractConfigData
from smellybot.config.abstract_definition import AbstractConfigDefinition
from smellybot.config.abstract_element import AbstractConfigElement
from smellybot.config.exceptions import ConfigNotSetException, OperationNotSupportedException
from smellybot.config.types import ConfigItemType


class MockConfigElement(AbstractConfigElement):
    def __init__(self, value: Any):
        self.value = value

    def get(self):
        return self.value

    def set(self, value: Any):
        pass

    def key_set(self, key: str, value: Any):
        pass

    def add(self, value: Any):
        pass

    def remove(self, value: Any):
        pass

    def notify(self, operation: str, value: Optional[Any]):
        pass

    def add_listener(self, operation: Optional[str], listener: Callable[[str, Any], None]):
        pass


class ConfigElement(AbstractConfigElement):
    def __init__(self, data: AbstractConfigData, definition: AbstractConfigDefinition, key: str, location: str,
                 ctype: ConfigItemType, superior: AbstractConfigElement):
        self.data = data
        self.definition = definition
        self.key = key
        self.location = location
        self.ctype = ctype
        self.superior = superior
        self.listeners: List[Tuple[List[str], Callable[[str, Any], None]]] = []

    def get(self):
        value = self._get()
        return self.ctype.from_store_format(value)

    def _get(self):
        value = self.data.get(self.key, self.location)
        if value is None:
            if self.superior:
                value = self.superior.get()
            else:
                raise ConfigNotSetException(self.key, self.location)
        return value

    def set(self, value: Any):
        parsed_value = self.ctype.parse(value)
        store_value = self.ctype.to_store_format(parsed_value)
        self._set(store_value)
        self.notify_all("set", value)
        self.data.save()

    def _set(self, value: Any):
        self.data.set(self.key, self.location, value)

    def add_listener(self, handler: Callable[[str, Any], None], operations: Optional[List[str]] = None):
        self.listeners.append((operations, handler))

    def notify(self, operation: str, value: Optional[Any]):
        for listener in self.listeners:
            if not listener[0] or operation in listener[0]:
                listener[1](operation, value)

    def notify_all(self, operation: str, value: Optional[Any]):
        self.definition.notify(self.location, operation, value)

    def key_set(self, key: str, value: Any):
        raise OperationNotSupportedException(
            f"The configuration {self.key} only supports the operations get, set and unset",
            f"Operation 'key_set' is not supported on config '{self.key}'"
        )

    def add(self, value: Any):
        raise OperationNotSupportedException(
            f"The configuration {self.key} only supports the operations get, set and unset",
            f"Operation 'add' is not supported on config '{self.key}'"
        )

    def remove(self, value: Any):
        raise OperationNotSupportedException(
            f"The configuration {self.key} only supports the operations get, set and unset",
            f"Operation 'remove' is not supported on config '{self.key}'"
        )


class ListConfigElement(ConfigElement):
    def __init__(self, data: AbstractConfigData, definition: AbstractConfigDefinition, key: str, location: str,
                 ctype: ConfigItemType, superior: AbstractConfigElement, unique: bool = False):
        super().__init__(data, definition, key, location, ctype, superior)
        self.unique = unique

    def get(self) -> List[Any]:
        values = []
        if self.superior:
            superior_values = self.superior.get()
            if superior_values:
                values += superior_values
        own_values = self.data.get(self.key, self.location)
        if own_values:
            values += own_values
        return [self.ctype.from_store_format(value) for value in values]

    def set(self, value: list):
        if not isinstance(value, list):
            raise ValueError()
        parsed_values = [self.ctype.to_store_format(self.ctype.parse(v)) for v in value]
        if self.unique:
            value_list = []
            [value_list.append(x) for x in parsed_values if x not in value_list]
        else:
            value_list = list(value)
        self.data.set(self.key, self.location, value_list)
        self.data.save()
        self.notify_all("set", value)

    def add(self, value: Any):
        value_list = self.data.get(self.key, self.location) or []
        if not self.unique or value not in value_list:
            parsed_value = self.ctype.parse(value)
            store_value = self.ctype.to_store_format(parsed_value)
            value_list.append(store_value)
        self.data.set(self.key, self.location, value_list)
        self.data.save()
        self.notify_all("add", value)

    def remove(self, value: Any):
        parsed_value = self.ctype.parse(value)
        store_value = self.ctype.to_store_format(parsed_value)
        value_list = self.data.get(self.key, self.location)
        value_list = [v for v in value_list if v != store_value]
        self.data.set(self.key, self.location, value_list)
        self.data.save()
        self.notify_all("remove", value)
