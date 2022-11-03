import re
from typing import Any

from smellybot.config.types import ConfigItemType, ConfigParseError


class CString(ConfigItemType):
    def parse(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        raise ConfigParseError("An unknown error occured", "Non-string value provided to string config type")


class CLowerString(CString):
    def parse(self, value: Any) -> str:
        string = super().parse(value)
        return string.lower()


class CUpperString(CString):
    def parse(self, value: Any) -> str:
        string = super().parse(value)
        return string.upper()


class CUsername(CLowerString):
    username_regex = re.compile(r'^[a-zA-Z0-9_]+$')

    def _parse(self, value: Any) -> str:
        string = super().parse(value)
        if self.username_regex.match(string):
            return string
        raise ConfigParseError(f'Value needs to be a valid twitch username (Only letters, numbers and underscores)',
                               f"Value '{value}' is not a valid username")
