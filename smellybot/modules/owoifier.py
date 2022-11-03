import random
import subprocess
from difflib import SequenceMatcher
from typing import cast

from smellybot.access_control import Everyone, ModPlus
from smellybot.bot_command import BotCommand, SuperCommand
from smellybot.bot_module import BotModule
from smellybot.config.definition import ListConfigDefinition
from smellybot.config.element import ListConfigElement
from smellybot.config.secure_config import Config
from smellybot.config.types.string import CUsername, CString
from smellybot.context import MessageContext


class Owoifier(BotModule):

    def __init__(self, config: Config, bot_channel):
        super().__init__(config, bot_channel)
        self.command_list()

        self.auto_targets: ListConfigElement = cast(ListConfigElement, config.register(
            ListConfigDefinition("owoifier.auto_targets", ctype=CUsername(), unique=True),
            read_access_control=ModPlus()
        ))

        self.endings: ListConfigElement = cast(ListConfigElement, config.register(
            ListConfigDefinition("owoifier.endings", ctype=CString(), unique=True),
            read_access_control=ModPlus()
        ))

    @classmethod
    def name(cls):
        return "owoifier"

    def command_list(self):
        self.add_command(BotCommand(Config("owoify", self.config), self, self.owoify, name="owoify", access_control=Everyone()))

        owoifier_command = SuperCommand(
            Config("owoifier", self.config),
            self,
            access_control=ModPlus(),
            name="owoifier"
        )

        target_command = BotCommand(
            Config("target", owoifier_command.config),
            self,
            self.target,
            access_control=ModPlus(),
            name="target"
        )

        untarget_command = BotCommand(
            Config("untarget", owoifier_command.config),
            self,
            self.untarget,
            access_control=ModPlus(),
            name="untarget"
        )

        owoifier_command.add_subcommand(target_command)
        owoifier_command.add_subcommand(untarget_command)

        self.add_command(owoifier_command)

    async def _handle_message(self, context: MessageContext):
        if context.author.username.lower() not in self.auto_targets.get():
            return
        if context.message.startswith("!"):
            return
        self.logger.info(f"{context.author.username}: {context.message}")
        owo_message = self.owoify_message(context.message)
        if not self.message_differs_significantly(context.message, owo_message):
            return
        owo_message = self.add_ending(owo_message)
        await self.bot_channel.send(owo_message)

    async def owoify(self, _context: MessageContext, arguments: str, _command: str, _head: str, **_kwargs):
        if arguments:
            await self.send_owo_message(arguments)
        elif self.bot_channel.context.previous_context.message:
            await self.send_owo_message(self.bot_channel.context.previous_context.message)

    async def target(self, _context: MessageContext, arguments: str, _command: str, _head: str, **_kwargs):
        self.auto_targets.add(arguments)

    async def untarget(self, _context: MessageContext, arguments: str, _command: str, _head: str, **_kwargs):
        self.auto_targets.remove(arguments)

    async def send_owo_message(self, message: str):
        owo_message = self.owoify_message(message)
        owo_message = self.add_ending(owo_message)
        await self.bot_channel.send(owo_message)

    def message_differs_significantly(self, original_message: str, owo_message: str):
        difference = 1 - SequenceMatcher(None, original_message.strip(), owo_message.strip()).ratio()
        return difference > 0.04

    def owoify_message(self, message: str):
        result = subprocess.run(['owoifier', "-t", message], capture_output=True)
        return result.stdout.decode("utf-8")

    def add_ending(self, message: str):
        separators = [", ", " "]
        endings = self.endings.get()

        if not endings:
            return message

        separator = random.choice(separators)
        ending = random.choice(endings)

        return message.rstrip() + separator + ending
