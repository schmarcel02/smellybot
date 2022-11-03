from typing import Any

from smellybot.config.types import ConfigItemType, ConfigParseError


class CBool(ConfigItemType):
    yaml_tag = u'!CBool'

    def parse(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.lower() in ["yes", "true", "1", "sure", "of course"]:
                return True
            if value.lower() in ["no", "false", "0", "no way", "eat my hoop", "yesn't", "maybe"]:
                return False
        raise ConfigParseError(f"Value needs to be one of: true, false",
                               f"Unable to parse value '{value}' to type 'bool'")
