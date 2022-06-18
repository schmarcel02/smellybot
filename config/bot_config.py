import logging
from typing import List

import yaml


def validate_config(config: dict):
    if "access_token" not in config or "bot_username" not in config \
            or "admin_users" not in config or "channels" not in config \
            or "master_user" not in config or "prefix" not in config:
        return False
    return True


class BotConfig:
    CONFIG_FILE_NAME = "config/config.yaml"

    def __init__(self, logger: logging.Logger, auto_save: bool = True):
        self.logger = logger
        self.auto_save = auto_save
        self.config = {
            "access_token": "",
            "bot_username": "",
            "prefix": "!",
            "admin_users": {

            },
            "channels": {

            }
        }

    def load(self):
        try:
            with open(self.CONFIG_FILE_NAME, "r") as quote_file:
                config = yaml.safe_load(quote_file)
        except Exception:
            self.logger.warning("Unable to load config file '%s':", self.CONFIG_FILE_NAME, exc_info=True)
            return False
        if not validate_config(config):
            self.logger.warning("Error in config file '%s':", self.CONFIG_FILE_NAME)
            return False
        self.config = config

    def save(self):
        with open(self.CONFIG_FILE_NAME, "w+") as config_file:
            yaml.safe_dump(self.config, config_file)

    def get_access_token(self) -> str:
        return self.config["access_token"]

    def get_bot_username(self) -> str:
        return self.config["bot_username"]

    def get_prefix(self) -> str:
        return self.config["prefix"]

    def get_channel(self, channel_name: str) -> 'ChannelConfig':
        module_dict = self.config["channels"].get(channel_name.lower())
        if not module_dict:
            self.add_channel(channel_name)
        return ChannelConfig(self, channel_name)

    def add_channel(self, channel_name: str):
        self.config["channels"][channel_name.lower()] = {
            "name": channel_name,
            "enabled": True,
            "mod_users": {

            },
            "modules": {

            }
        }
        self.save()

    def get_channels(self) -> List['ChannelConfig']:
        return [ChannelConfig(self, channel_name) for channel_name in self.config["channels"]]

    def add_admin_user(self, username: str):
        self.config["admin_users"][username.lower()] = True
        self.save()

    def remove_admin_user(self, username: str):
        if username.lower() not in self.config["admin_users"]:
            return
        del self.config["admin_users"][username.lower()]
        self.save()

    def is_admin_user(self, username: str):
        return self.config["admin_users"].get(username.lower(), False)

    def get_master_user(self):
        return self.config["master_user"]

    def is_master_user(self, username: str):
        return self.config["master_user"].lower() == username.lower()

    def is_bot_user(self, username: str):
        return self.config["bot_username"].lower() == username.lower()


class ChannelConfig:
    def __init__(self, bot_config: BotConfig, channel_name: str):
        self.bot_config = bot_config
        self.channel_config = bot_config.config["channels"][channel_name.lower()]
        self.channel_name = channel_name

    def get_channel_name(self):
        return self.channel_config["name"]

    def get_module(self, module_name: str):
        module_dict = self.channel_config["modules"].get(module_name.lower())
        if not module_dict:
            self.add_module(module_name)
        return ModuleConfig(self.bot_config, self, module_name)

    def add_module(self, module_name: str):
        self.channel_config["modules"][module_name.lower()] = {
            "module_name": module_name,
            "enabled": False,
            "commands": {

            }
        }
        self.bot_config.save()

    def set_enabled(self, enabled: bool):
        self.channel_config["enabled"] = enabled
        self.bot_config.save()

    def is_enabled(self):
        return self.channel_config["enabled"]

    def add_mod_user(self, username: str):
        self.channel_config["mod_users"][username.lower()] = True
        self.bot_config.save()

    def remove_mod_user(self, username: str):
        if username.lower() not in self.channel_config["mod_users"]:
            return
        del self.channel_config["mod_users"][username.lower()]
        self.bot_config.save()

    def is_mod_user(self, username: str):
        return self.channel_config["mod_users"].get(username.lower(), False)

    def is_streamer(self, username: str):
        return self.channel_config["name"].lower() == username.lower()


class ModuleConfig:
    def __init__(self, bot_config: BotConfig, channel_config: ChannelConfig, module_name: str):
        self.bot_config = bot_config
        self.channel_config = channel_config
        self.module_config = channel_config.channel_config["modules"][module_name.lower()]
        self.module_name = module_name

    def get_command(self, command_name: str):
        command_dict = self.module_config["commands"].get(command_name.lower())
        if not command_dict:
            self.add_command(command_name)
        return CommandConfig(self.bot_config, self, command_name)

    def add_command(self, command_name: str):
        self.module_config["commands"][command_name.lower()] = {
            "command_name": command_name,
            "enabled": True
        }
        self.bot_config.save()

    def set_enabled(self, enabled: bool):
        self.module_config["enabled"] = enabled
        self.bot_config.save()

    def is_enabled(self):
        return self.module_config["enabled"]


class CommandConfig:
    def __init__(self, bot_config: BotConfig, module_config: ModuleConfig, command_name: str):
        self.bot_config = bot_config
        self.module_config = module_config
        self.command_config = module_config.module_config["commands"][command_name.lower()]
        self.command_name = command_name

    def set_enabled(self, enabled: bool):
        self.command_config["enabled"] = enabled
        self.bot_config.save()

    def is_enabled(self):
        return self.command_config["enabled"]
