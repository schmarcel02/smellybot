from typing import Any

from smellybot.config.types import ConfigItemType, ConfigParseError


class CInt(ConfigItemType):
    def parse(self, value: Any) -> int:
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            return int(value)
        raise ConfigParseError(f"Value needs to be a whole number",
                               f"Unable to convert value '{value}' to type 'int'")


class CBoundedInt(CInt):
    def __init__(self, lower_bound: int, upper_bound: int):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def parse(self, value: Any) -> int:
        int_value = super().parse(value)
        if self.lower_bound <= int_value <= self.upper_bound:
            return int_value
        raise ConfigParseError(f"Value needs to be between {self.lower_bound} and {self.upper_bound}")
