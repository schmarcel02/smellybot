from typing import Any

import yaml

from smellybot.config.abstract_data import AbstractConfigData


class ConfigData(AbstractConfigData):
    def __init__(self, filename: str):
        self._filename = filename
        self._data = {}

    def load(self):
        with open(self._filename, "r") as config_file:
            self._data = yaml.load(config_file, Loader=yaml.Loader)

    def save(self):
        with open(self._filename, "w+") as config_file:
            yaml.dump(self._data, config_file, Dumper=yaml.Dumper)

    def get(self, key: str, location: str):
        if location not in self._data:
            return None
        local_data = self._data[location]
        if key not in local_data:
            return None
        return local_data[key]

    def set(self, key: str, location: str, value: Any):
        if location not in self._data:
            self._data[location] = {}
        self._data[location][key] = value
