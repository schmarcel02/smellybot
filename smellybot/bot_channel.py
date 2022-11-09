import logging
from logging import Logger
from typing import Dict, Optional, cast

from datetime import datetime

from twitchio import Channel, Chatter, Message
from twitchio.ext.commands import Context

from config import smelly_logger
from smellybot.channel_context import ChannelContext
from smellybot.config.definition import ListConfigDefinition
from smellybot.config.element import ListConfigElement
from smellybot.config.secure_config import Config
from smellybot.config.types.string import CLowerString
from smellybot.modules import ModuleMaster
from smellybot.abstract_classes import AbstractChannel, AbstractModule
from smellybot.access_control import ModPlus
from smellybot.context import MessageContext, BotUser


class BotChannel(AbstractChannel):
    def __init__(self, config: Config, bot, name: str):
        config.register(ListConfigDefinition("channel.modules", unique=True, ctype=CLowerString()),
                        read_access_control=ModPlus())

        self.channel_modules_config = cast(ListConfigElement, config.element("channel.modules"))
        self.bot_user_config = config.element("bot_username")
        self.master_user_config = config.element("master_user")
        self.admin_users_config = cast(ListConfigElement, config.element("admin_users"))
        self.mod_users_config = cast(ListConfigElement, config.element("mod_users"))
        self.enabled_config = config.element("enabled")

        self.logger = logging.LoggerAdapter(smelly_logger, extra={"channel_name": name})
        self.config = config
        self.bot = bot
        self.name = name
        self.context = ChannelContext()
        self.twitch_channel = None

        self.last_message_datetime = datetime.fromtimestamp(0)

        self.modules: Dict[str, AbstractModule] = {}
        self.commands: Dict[str, Dict[str, AbstractModule]] = {}

        initial_modules = self.channel_modules_config.get()
        for module_name in initial_modules:
            self.add_module(module_name)

    async def set_twitch_channel(self, twitch_channel: Channel):
        self.twitch_channel = twitch_channel
        for module in self.modules.values():
            await module.on_ready()

    def get_bot_module(self, name: str) -> Optional[AbstractModule]:
        return self.modules.get(name)

    def add_module(self, module_name: str):
        module_name = module_name.lower()
        module_class = ModuleMaster.get_module_by_name(module_name)

        if module_name not in self.modules:
            module_config = Config(module_name, self.config)
            self.modules[module_name] = module_class(module_config, self)

    async def remove_module(self, module_name: str):
        module_name = module_name.lower()
        if module_name in self.modules:
            del self.modules[module_name]
        for modules in self.commands.values():
            if module_name in modules:
                del modules[module_name]

    def register_command(self, command_name: str, module: AbstractModule):
        command_name = command_name.lower()
        module_name = module.name().lower()

        if command_name not in self.commands:
            self.commands[command_name] = {}
        self.commands[command_name][module_name] = module

        self.bot.register_command(command_name)

    async def remove_command(self, command_name: str, module: AbstractModule):
        command_name = command_name.lower()
        module_name = module.name().lower()

        if command_name in self.commands and module_name in self.commands[command_name]:
            del self.commands[command_name][module_name]

    def build_user(self, api_user: Chatter):
        author = BotUser(api_user.display_name)
        if author.username.lower() == self.master_user_config.get():
            author.add_role("master")
        admin_users = [username.lower() for username in self.admin_users_config.get()]
        if author.username.lower() in admin_users:
            author.add_role("admin")
        if author.username.lower() == self.name.lower():
            author.add_role("streamer")
        mod_users = [username.lower() for username in self.mod_users_config.get()]
        if api_user.is_mod or author.username.lower() in mod_users:
            author.add_role("mod")
        if api_user.is_subscriber:
            author.add_role("sub")
        return author

    def build_context(self, api_user: Chatter, message: str):
        author = self.build_user(api_user)
        return MessageContext(self.bot, self, author, message)

    async def run_command(self, command_name: str, ctx: Context):
        message_context = self.build_context(ctx.author, ctx.message.content)
        if not self.enabled_config.get() and command_name.lower() not in ["smelsadmin", "smelsmod"]:
            self.logger.info(f"{ctx.author.name}: {ctx.message.content}")
            self.logger.warning("Bot is disabled in this channel")
            await self.send_warning(
                f"{self.bot_user_config.get()} is disabled. "
                f"Mods can type '!smelsmod enable' to enable it",
                message_context
            )
            return

        modules = self.commands.get(command_name.lower())
        if not modules:
            self.logger.warning("Channel has no command '%s'", command_name)
            return

        for module in modules.values():
            await module.run_command(command_name.lower(), message_context)

    async def send(self, message: str):
        self.logger.info(f"Sending: {message}")
        await self.twitch_channel.send(message)

    async def send_info(self, message: str, context: MessageContext):
        if ModPlus().check(context.author):
            await self.send(message)

    async def send_warning(self, message: str, context: MessageContext):
        if ModPlus().check(context.author):
            await self.send(message)

    async def handle_message(self, message: Message):
        if not self.enabled_config.get():
            return
        message_context = self.build_context(message.author, message.content)
        self.context.previous_context = self.context.current_context
        self.context.current_context = message_context
        if message.echo:
            return
        for module in self.modules.values():
            await module.handle_message(message_context)

    async def handle_usernotice(self, author_username: str, tags: dict):
        if not self.enabled_config.get():
            return
        for module in self.modules.values():
            await module.handle_usernotice(author_username, tags)
