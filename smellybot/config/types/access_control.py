from typing import Any

from smellybot.access_control import *
from smellybot.config.types import ConfigItemType, ConfigParseError


class CAccessControl(ConfigItemType):
    access_control_factories = {}

    def parse(self, value: Any) -> AccessControl:
        if isinstance(value, AccessControl):
            return value
        if isinstance(value, str):
            access_control_factory = self.access_control_factories.get(value.lower())
            if access_control_factory:
                return access_control_factory()
        raise ConfigParseError("Value must be one of: " + ", ".join(self.access_control_factories.keys()),
                               f"Unable to parse value '{value}' to type 'AccessControl'")

    def to_store_format(self, value: AccessControl) -> str:
        return value.name()

    def from_store_format(self, value: str) -> Any:
        return self.parse(value)


CAccessControl.access_control_factories[Everyone.name()] = Everyone
CAccessControl.access_control_factories[MasterOnly.name()] = MasterOnly
CAccessControl.access_control_factories[AdminOnly.name()] = AdminOnly
CAccessControl.access_control_factories[StreamerOnly.name()] = StreamerOnly
CAccessControl.access_control_factories[ModOnly.name()] = ModOnly
CAccessControl.access_control_factories[AdminPlus.name()] = AdminPlus
CAccessControl.access_control_factories[StreamerPlus.name()] = StreamerPlus
CAccessControl.access_control_factories[ModPlus.name()] = ModPlus
