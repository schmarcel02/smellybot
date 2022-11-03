from typing import Any

from smellybot.config.types import ConfigItemType, ConfigParseError


class CFloat(ConfigItemType):
    def parse(self, value: Any) -> float:
        if isinstance(value, float):
            return value
        if isinstance(value, str):
            return float(value)
        raise ConfigParseError(f"Value needs to be a decimal number",
                               f"Unable to convert value '{value}' to type 'float'")


class CBoundedFloat(CFloat):
    def __init__(self, lower_bound: float, upper_bound: float):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def parse(self, value: Any) -> float:
        float_value = super().parse(value)
        if self.lower_bound <= float_value <= self.upper_bound:
            return float_value
        raise ConfigParseError(f"Value needs to be between {self.lower_bound} and {self.upper_bound}")
