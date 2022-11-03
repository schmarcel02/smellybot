from typing import List, Optional, Any

from smellybot.access_control import AccessControl, AdminPlus, ModPlus, Everyone
from smellybot.bot_command import BotCommand, SuperCommand
from smellybot.bot_module import BotModule
from smellybot.config.abstract_element import AbstractConfigElement
from smellybot.config.element import ListConfigElement, MockConfigElement
from smellybot.config.secure_config import Config
from smellybot.context import MessageContext


class Controller(BotModule):

    def __init__(self, config: Config, bot_channel):
        super().__init__(config, bot_channel)
        self.command_list()
        self.enabled_config = MockConfigElement(True)

    @classmethod
    def name(cls):
        return "controller"

    def command_list(self):
        smellyadmin_command = SuperCommand(
            Config("smelsadmin", self.config),
            self,
            access_control=AdminPlus(),
            name="smelsadmin",
            attributes={"config": self.config.root}
        )
        smellyadmin_command.enabled_config = MockConfigElement(True)

        smellymod_command = SuperCommand(
            Config("smelsmod", self.config),
            self,
            access_control=ModPlus(),
            name="smelsmod",
            attributes={"config": self.config.parent}
        )
        smellymod_command.enabled_config = MockConfigElement(True)

        smellybot_command = SuperCommand(
            Config("smelsbot", self.config),
            self,
            access_control=Everyone(),
            name="smelsbot",
            attributes={"config": self.config.parent}
        )
        smellybot_command.enabled_config = MockConfigElement(True)

        config_command = BotCommand(
            Config("config", self.config),
            self,
            self.cmd_config,
            access_control=ModPlus(),
            name="config"
        )
        config_command.enabled_config = MockConfigElement(True)

        shutdown_command = BotCommand(
            Config("shutdown", self.config),
            self,
            self.shutdown,
            access_control=AdminPlus(),
            name="shutdown"
        )
        shutdown_command.enabled_config = MockConfigElement(True)

        add_channel_command = BotCommand(
            Config("add_channel", self.config),
            self,
            self.add_channel,
            access_control=AdminPlus(),
            name="add_channel"
        )
        shutdown_command.enabled_config = MockConfigElement(True)

        enable_command = BotCommand(
            Config("enable", self.config),
            self,
            self.set_enabled,
            access_control=ModPlus(),
            name="enable",
            attributes={"enabled": True}
        )
        enable_command.enabled_config = MockConfigElement(True)

        disable_command = BotCommand(
            Config("disable", self.config),
            self,
            self.set_enabled,
            access_control=ModPlus(),
            name="disable",
            attributes={"enabled": False}
        )
        disable_command.enabled_config = MockConfigElement(True)

        smellyadmin_command.add_subcommand(config_command)
        smellymod_command.add_subcommand(config_command)

        smellyadmin_command.add_subcommand(enable_command)
        smellymod_command.add_subcommand(enable_command)
        smellyadmin_command.add_subcommand(disable_command)
        smellymod_command.add_subcommand(disable_command)

        smellyadmin_command.add_subcommand(shutdown_command)

        smellyadmin_command.add_subcommand(add_channel_command)

        self.add_command(smellymod_command)
        self.add_command(smellyadmin_command)

    async def _handle_message(self, context: MessageContext):
        pass
        
    async def cmd_config(self, context: MessageContext, arguments: str, _command: str, head: str, config: Config, **_kwargs):
        arguments_split = arguments.split(maxsplit=2)

        try:
            operation = arguments_split[0]
            if operation not in ["get", "set", "unset", "add", "remove"]:
                raise ValueError()
        except IndexError or ValueError:
            self.logger.warning("No operation provided")
            await self.bot_channel.send(f"Usage: !{head} get/set/unset/add/remove {{location}}:{{key}} {{value}}")
            return
        except ValueError:
            self.logger.warning("Invalid operation provided")
            await self.bot_channel.send(f"Usage: !{head} get/set/unset/add/remove {{location}}:{{key}} {{value}}")
            return

        try:
            location_and_key = arguments_split[1].split(":")
        except IndexError:
            self.logger.warning("No location and key provided")
            await self.bot_channel.send(f"Usage: !{head} {operation} {{location}}:{{key}} {{value}}")
            return

        if operation not in ["get", "unset"]:
            try:
                value = arguments_split[2]
            except IndexError:
                self.logger.warning("No value provided")
                await self.bot_channel.send(f"Usage: !{head} {operation} {location_and_key} {{value}}")
                return

        if len(location_and_key) > 1:
            location = location_and_key[0]
            key = location_and_key[1]
        else:
            location = None
            key = location_and_key[0]

        if operation == "get":
            self.bot_channel.send(config_get(config, location, key, context))
            return
        elif operation == "set":
            config_set(config, location, key, value, context)
        elif operation == "unset":
            config_unset(config, location, key, context)
        elif operation == "add":
            config_add(config, location, key, value, context)
        elif operation == "remove":
            config_remove(config, location, key, value, context)
        else:
            self.logger.warning(f"Invalid operation: '{operation}'")
            await self.bot_channel.send_info(f"Invalid operation: '{operation}'", context)
            return

        await self.bot_channel.send_info(f"Successfully updated configuration", context)

    async def set_enabled(self, context: MessageContext, arguments: str, _command: str, _head: str, config: Config, enabled: bool, **_kwargs):
        config_set(config, arguments, "enabled", enabled, context)

        if enabled:
            if not arguments:
                await self.bot_channel.send_info(f"*Windows XP startup sound*", context)
            else:
                await self.bot_channel.send_info(f"Successfully enabled {arguments}", context)
        else:
            if not arguments:
                await self.bot_channel.send_info(f"*dies peacefully*", context)
            else:
                await self.bot_channel.send_info(f"Successfully enabled {arguments}", context)

    async def shutdown(self, context: MessageContext, _arguments: str, _command: str, _head: str, **_kwargs):
        await self.bot_channel.send_info("*dies in pain*", context)
        exit(0)

    async def add_channel(self, _context: MessageContext, arguments: str, _command: str, _head: str, **_kwargs):
        channel_name = arguments.lower()
        self.bot_channel.bot.join_channel(channel_name)


def config_get(config: Config, location: str, key: str, context: MessageContext):
    local_config = resolve_location_string(config, location, context)
    element = local_config.element(key)
    return element.get()

def config_set(config: Config, location: str, key: str, value: Optional[Any], context: MessageContext):
    local_config = resolve_location_string(config, location, context)
    element = local_config.element(key)
    if isinstance(element, ListConfigElement):
        raise Exception("Can't set a list config")
    element.set(value)


def config_unset(config: Config, location: str, key: str, context: MessageContext):
    local_config = resolve_location_string(config, location, context)
    element = local_config.element(key)
    if isinstance(element, ListConfigElement):
        raise Exception("Can't unset a list config")
    config_set(config, location, key, None, context)


def config_add(config: Config, location: str, key: str, value: Optional[str], context: MessageContext):
    local_config = resolve_location_string(config, location, context)
    element = local_config.element(key)
    if not isinstance(element, ListConfigElement):
        raise Exception("Can't add to a non-list config")
    element.add(value)


def config_remove(config: Config, location: str, key: str, value: Optional[str], context: MessageContext):
    local_config = resolve_location_string(config, location, context)
    element = local_config.element(key)
    if not isinstance(element, ListConfigElement):
        raise Exception("Can't remove from a non-list config")
    element.remove(value)


def resolve_location_string(config: Config, location: str, context: MessageContext):
    if not location:
        return config
    location_split = location.strip(".").split(".")
    return resolve_location(config, location_split, context)


def resolve_location(config: Config, location: List[str], context: MessageContext):
    if not location:
        return config
    child = config.get_child(location[0])
    if not child.check(context):
        raise Exception()
    if len(location) == 1:
        return child
    return resolve_location(child, location[1:], context)
