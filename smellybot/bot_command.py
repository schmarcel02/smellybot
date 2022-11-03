import logging
from typing import Dict, Callable, Coroutine, List, Any

from smellybot.abstract_classes import AbstractCommand
from smellybot.access_control import AccessControl, Everyone
from smellybot.bot_module import BotModule
from smellybot.config.secure_config import Config
from smellybot.context import MessageContext


class BotCommand(AbstractCommand):
    def get_name_and_aliases(self) -> List[str]:
        return [self.name] + self.aliases

    def __init__(self, config: Config, bot_module: BotModule,
                 func: Callable[[MessageContext, str, str, str, ...], Coroutine], name: str,
                 aliases: List[str] = None,
                 access_control: AccessControl = Everyone(),
                 attributes: Dict[str, Any] = None):
        self.config = config

        self.enabled_config = config.element("enabled")

        self.bot_module = bot_module
        self.func = func
        self.access_control = access_control
        self.name = name
        self.aliases: List[str] = aliases or []
        self.attributes: Dict[str, Any] = attributes or {}

        self.logger = logging.LoggerAdapter(
            bot_module.logger,
            extra={
                "channel_name": bot_module.bot_channel.name,
                "module_name": bot_module.name(),
                "command_name": self.name
            }
        )

    async def invoke(self, context: MessageContext, arguments: str, command: str, head: str, **kwargs):
        if not self.access_control.check(context.author):
            self.logger.warning("User '%s' is not allowed to use this command", context.author.display_name)
            return
        if not self.enabled_config.get() and head[1:].split(" ", maxsplit=1)[0].lower() not in ["smelsadmin", "smelsmod"]:
            self.logger.warning("Command is disabled")
            await self.bot_module.bot_channel.send_warning(f"Command '{self.name}' is disabled", context)
            return

        sub_attributes = kwargs.copy()
        sub_attributes.update(self.attributes)
        await self.func(context, arguments, command, head, **sub_attributes)


class SuperCommand(BotCommand):
    def __init__(self, config: Config, bot_module: BotModule, name: str, aliases: List[str] = None,
                 access_control: AccessControl = Everyone(), attributes: Dict[str, Any] = None):
        super().__init__(config, bot_module, self.route, name, aliases, access_control, attributes)
        self.subcommands: Dict[str, BotCommand] = {}

    def add_subcommand(self, command: BotCommand):
        for alias in [command.name] + command.aliases:
            self.subcommands[alias] = command

    async def route(self, context: MessageContext, arguments: str, _command: str, head: str, **kwargs):
        arguments_split = arguments.split(" ", 1)
        subcommand_name = arguments_split[0]
        try:
            subarguments = arguments_split[1]
        except IndexError:
            subarguments = ""

        subcommand = self.subcommands.get(subcommand_name)
        if not subcommand:
            self.logger.warning(f"Command has no subcommand '{subcommand_name}'")
            return

        await subcommand.invoke(context, subarguments, subcommand_name, head + " " + subcommand_name, **kwargs)
