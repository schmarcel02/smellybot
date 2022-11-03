from typing import Dict

from smellybot.config.abstract_definition import AbstractConfigDefinition
from smellybot.config.abstract_schema import AbstractConfigSchema


class ConfigSchema(AbstractConfigSchema):
    def __init__(self):
        self.schema: Dict[str, AbstractConfigDefinition] = {}

    def register(self, definition: AbstractConfigDefinition):
        if definition.key not in self.schema:
            self.schema[definition.key] = definition
        return self.schema[definition.key]

    def get_definition(self, key: str) -> AbstractConfigDefinition:
        return self.schema.get(key)
