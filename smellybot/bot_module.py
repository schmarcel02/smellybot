import logging
from abc import ABC, abstractmethod
from typing import Dict

from smellybot.logger.smelly_logger import slogger
from smellybot.abstract_classes import AbstractCommand, AbstractModule
from smellybot.config.secure_config import Config
from smellybot.context import MessageContext


class BotModule(AbstractModule, ABC):
    def __init__(self, config: Config, bot_channel):
        self.config = config

        self.enabled_config = config.element("enabled")

        self.bot_channel = bot_channel
        self.logger = logging.LoggerAdapter(
            slogger,
            extra={
                "channel_name": bot_channel.name,
                "module_name": self.name()
            }
        )
        self.commands: Dict[str, AbstractCommand] = {}

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        pass

    def add_command(self, command: AbstractCommand):
        for alias in command.get_name_and_aliases():
            self.commands[alias] = command
            self.bot_channel.register_command(alias, self)

    async def run_command(self, command_name: str, context: MessageContext):
        self.logger.info(f"{context.author.username}: {context.message}")
        if not self.enabled_config.get() and command_name.lower() not in ["smelsadmin", "smelsmod"]:
            self.logger.warning("Module is disabled")
            await self.bot_channel.send_warning(
                f"Module '{self.name()}' is disabled. "
                f"Mods can write '!smelsmod enable {self.name()}' to enable it",
                context
            )
            return

        command = self.commands.get(command_name)
        if not command:
            self.logger.warning("Module has no command '%s'", command_name)
            return

        command_split = context.message.split(" ", 1)
        try:
            head = command_split[0]
        except IndexError:
            head = ""
        try:
            arguments = command_split[1]
        except IndexError:
            arguments = ""

        await command.invoke(context, arguments=arguments, command=command_name, head=head)

    async def on_ready(self):
        pass

    async def handle_message(self, context: MessageContext):
        if self.enabled_config.get():
            await self._handle_message(context)

    async def _handle_message(self, context: MessageContext):
        pass

    async def handle_usernotice(self, author_username: str, tags: dict):
        if self.enabled_config.get():
            await self._handle_usernotice(author_username, tags)

    async def _handle_usernotice(self, author_username: str, tags: dict):
        pass
