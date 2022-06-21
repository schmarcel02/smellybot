import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Callable, List, Coroutine, Tuple, Union, Type

from twitchio import Message, Channel

from twitchio.ext.commands import Context, Command, Bot

from config import smelly_logger, BotConfig, ChannelConfig, ModuleConfig, CommandConfig


class ChannelRouterCommand(Command):
    def __init__(self, smelly_bot: 'SmellyBot', command_name: str):
        super().__init__(command_name, self.command)
        self.smelly_bot = smelly_bot

    async def command(self, ctx: Context):
        channel_name = ctx.channel.name.lower()
        channel = self.smelly_bot.channels.get(channel_name)
        if not channel:
            smelly_logger.error("Channel '%s' not found", channel_name, exc_info=True)
        await channel.run_command(self.name, ctx)


class ModuleMaster:
    def __init__(self):
        self.modules: Dict[str, Type['BotModule']] = {}

    def add_module(self, module_class: Type['BotModule']):
        self.modules[module_class.name().lower()] = module_class


class AccessControl(Enum):
    @staticmethod
    def EVERYONE(command_config: CommandConfig, author):
        return True

    @staticmethod
    def MOD_PLUS(command_config: CommandConfig, author):
        return AccessControl.is_master(command_config, author) or \
            AccessControl.is_admin(command_config, author) or \
            AccessControl.is_streamer(command_config, author) or \
            AccessControl.is_mod(command_config, author)

    @staticmethod
    def STREAMER_PLUS(command_config: CommandConfig, author):
        return AccessControl.is_master(command_config, author) or \
            AccessControl.is_admin(command_config, author) or \
            AccessControl.is_streamer(command_config, author)

    @staticmethod
    def ADMIN_PLUS(command_config: CommandConfig, author):
        return AccessControl.is_master(command_config, author) or \
            AccessControl.is_admin(command_config, author)

    @staticmethod
    def STREAMER_ONLY(command_config: CommandConfig, author):
        return AccessControl.is_streamer(command_config, author)

    @staticmethod
    def ADMIN_ONLY(command_config: CommandConfig, author):
        return AccessControl.is_admin(command_config, author)

    @staticmethod
    def MASTER_ONLY(command_config: CommandConfig, author):
        return AccessControl.is_master(command_config, author)

    @staticmethod
    def is_mod(command_config, author):
        return command_config.module_config.channel_config.is_mod_user(author.name) or author.is_mod

    @staticmethod
    def is_streamer(command_config, author):
        return command_config.module_config.channel_config.is_streamer(author.name)

    @staticmethod
    def is_admin(command_config, author):
        return command_config.bot_config.is_admin_user(author.name)

    @staticmethod
    def is_master(command_config, author):
        return command_config.bot_config.is_master_user(author.name)

    def __call__(self, command_config, author):
        return self.value()


class BotCommand:
    def __init__(self, bot_module: 'BotModule', func: Callable[[Context, str, str, str], Coroutine],
                 access_control: AccessControl, name: str, aliases: List[str] = None):
        self.bot_module = bot_module
        self.func = func
        self.name = name or func.__name__.lower()
        self.command_config = bot_module.module_config.get_command(self.name)
        self.aliases: List[str] = aliases or []
        self.access_control = access_control
        self.logger = logging.LoggerAdapter(
            smelly_logger,
            extra={
                "channel_name": self.bot_module.bot_channel.channel_name,
                "module_name": self.bot_module.name(),
                "command_name": self.name
            }
        )

    async def activate(self):
        self.command_config.set_enabled(True)
        self.logger.info("Enabled command")
        await self.bot_module.bot_channel.send(f"Enabled command: {self.name}")

    async def deactivate(self):
        self.command_config.set_enabled(False)
        self.logger.info("Disabled command")
        await self.bot_module.bot_channel.send(f"Disabled command: {self.name}")

    async def invoke(self, ctx: Context, arguments: str, command: str, head: str):
        if not self.access_control(self.command_config, ctx.author):
            self.logger.warning("User '%s' is not allowed to use this command")
            return
        if not self.command_config.is_enabled() and not self.name.lower() == "smellybot":
            self.logger.warning("Command is disabled")
            if self.command_config.module_config.channel_config.is_streamer(ctx.author.name) \
                    or self.command_config.module_config.channel_config.is_mod_user(ctx.author.name) \
                    or ctx.author.is_mod:
                await self.bot_module.bot_channel.send(f"Command '{self.name}' is disabled")
            return
        await self.func(ctx, arguments, command, head)


class SuperCommand(BotCommand):
    def __init__(self, bot_module: 'BotModule', access_control: AccessControl, name: str, aliases: List[str] = None):
        super().__init__(bot_module, self.route, access_control, name, aliases)
        self.subcommands: Dict[str, BotCommand] = {}

    def add_subcommand(self, command: BotCommand):
        for alias in [command.name] + command.aliases:
            self.subcommands[alias] = command

    async def route(self, ctx: Context, arguments: str, command: str, head: str):
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
        await subcommand.invoke(ctx, subarguments, subcommand_name, head + " " + command)


class BotModule(ABC):
    def __init__(self, bot_channel: 'BotChannel', module_config: ModuleConfig):
        self.bot_channel = bot_channel
        self.module_config = module_config
        self.logger = logging.LoggerAdapter(
            smelly_logger,
            extra={
                "channel_name": bot_channel.channel_name,
                "module_name": self.name()
            }
        )
        self.commands: Dict[str, BotCommand] = {}

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        pass

    async def activate(self):
        self.module_config.set_enabled(True)
        self.logger.info("Activated module")
        await self.bot_channel.send(f"Enabled module: {self.name()}")

    async def deactivate(self):
        self.module_config.set_enabled(False)
        self.logger.info("Deactivated module")
        await self.bot_channel.send(f"Disabled module: {self.name()}")

    def add_command(self, func: Callable[[Context, str, str, str], Coroutine],
                    access_control: AccessControl = AccessControl.EVERYONE,
                    name: str = None, aliases: List[str] = None):
        command = BotCommand(self, func, access_control, name, aliases)
        for alias in command.aliases + [command.name]:
            self.commands[alias] = command

    def add_command_object(self, command: BotCommand):
        for alias in command.aliases + [command.name]:
            self.commands[alias] = command

    async def run_command(self, command_name: str, ctx: Context):
        self.logger.info(f"{ctx.author.name}: {ctx.message.content}")
        if not self.module_config.is_enabled() and not command_name.lower() == "smellybot":
            self.logger.warning("Module is disabled")
            if self.module_config.channel_config.is_streamer(ctx.author.name) \
                    or self.module_config.channel_config.is_mod_user(ctx.author.name) \
                    or ctx.author.is_mod:
                await self.bot_channel.send(f"Module '{self.name()}' is disabled")
            return
        command = self.commands.get(command_name)
        if not command:
            self.logger.warning("Module has no command '%s'", command_name)
            return
        command_split = ctx.message.content.split(" ", 1)
        try:
            arguments = command_split[1]
        except IndexError:
            arguments = ""

        await command.invoke(ctx, arguments, command_name, command_name)

    async def on_ready(self):
        pass

    async def _handle_message(self, message: Message):
        if self.module_config.is_enabled():
            await self.handle_message(message)

    async def handle_message(self, message: Message):
        pass

    async def _handle_usernotice(self, author_username: str, tags: dict):
        if self.module_config.is_enabled():
            await self.handle_usernotice(author_username, tags)

    async def handle_usernotice(self, author_username: str, tags: dict):
        pass


class BotChannel:
    def __init__(self, smelly_bot: 'SmellyBot', channel_config: ChannelConfig):
        self.smelly_bot = smelly_bot
        self.channel_config = channel_config
        self.channel_name = channel_config.get_channel_name()
        self.logger = logging.LoggerAdapter(smelly_logger, extra={"channel_name": self.channel_name})

        self.modules: Dict[str, BotModule] = {}
        self.commands: Dict[str, BotModule] = {}

        for module_name, module_class in smelly_bot.module_master.modules.items():
            module_config = channel_config.get_module(module_name)
            module = module_class(self, module_config)
            self.add_module(module)

        self.channel = None

    async def activate(self):
        self.channel_config.set_enabled(True)
        self.logger.info("Activated bot in channel")
        await self.send("Enabled SMELsBot")

    async def deactivate(self):
        self.channel_config.set_enabled(False)
        self.logger.info("Deactivated bot in channel")
        await self.send("Disabled SMELsBot")

    def add_module(self, bot_module: BotModule):
        self.modules[bot_module.name().lower()] = bot_module
        for command in bot_module.commands.values():
            for alias in command.aliases + [command.name]:
                self.commands[alias] = bot_module

    async def set_twitch_channel(self, channel: Channel):
        self.channel = channel
        for module in self.modules.values():
            await module.on_ready()

    async def run_command(self, command_name: str, ctx: Context):
        if not self.channel_config.is_enabled() and not command_name.lower() == "smellybot":
            self.logger.warning("Bot is disabled in this channel")
            if self.channel_config.is_streamer(ctx.author.name) or self.channel_config.is_mod_user(ctx.author.name) \
                    or ctx.author.is_mod:
                await self.send("Bot is disabled in this channel")
            return
        module = self.commands.get(command_name)
        if not module:
            self.logger.warning("Channel has no command '%s'", command_name)
            return
        await module.run_command(command_name, ctx)

    async def send(self, message: str):
        self.logger.info(f"Sending: {message}")
        await self.channel.send(message)

    async def handle_message(self, message: Message):
        if not self.channel_config.is_enabled():
            return
        for module in self.modules.values():
            await module._handle_message(message)

    async def handle_usernotice(self, author_username: str, tags: dict):
        if not self.channel_config.is_enabled():
            return
        for module in self.modules.values():
            await module._handle_usernotice(author_username, tags)


class SmellyBot(Bot):
    def __init__(self, module_master: ModuleMaster, bot_config: BotConfig, channels: List[str] = None):
        self.module_master = module_master
        self.bot_config = bot_config

        self.channels: Dict[str, BotChannel] = {}

        if channels:
            channel_configs = [bot_config.get_channel(channel_name) for channel_name in channels]
        else:
            channel_configs = bot_config.get_channels()

        super().__init__(token=bot_config.get_access_token(), prefix=bot_config.get_prefix(),
                         initial_channels=[channel_config.get_channel_name() for channel_config in channel_configs])

        for channel_config in channel_configs:
            bot_channel = BotChannel(self, channel_config)
            self.channels[bot_channel.channel_name.lower()] = bot_channel
            self.register_channel_commands(bot_channel)

    def join_channel(self, channel_name: str):
        self.loop.create_task(self.join_channels([channel_name]))

    def register_channel_commands(self, bot_channel: BotChannel):
        for module in bot_channel.modules.values():
            for command in module.commands.values():
                for alias in command.aliases + [command.name]:
                    if alias not in self.commands:
                        self.add_command(ChannelRouterCommand(self, alias))

    def add_bot_channel(self, bot_channel: BotChannel):
        self.channels[bot_channel.channel_name.lower()] = bot_channel
        self.register_channel_commands(bot_channel)
        self.join_channel(bot_channel.channel_name)

    async def event_join(self, twitch_channel: Channel, user):
        bot_channel = self.channels.get(twitch_channel.name.lower())
        if bot_channel and bot_channel.channel is None:
            print(f'Joined channel: {bot_channel.channel_name}')
            await bot_channel.set_twitch_channel(twitch_channel)

    async def event_message(self, message: Message):
        if message.echo:
            return

        channel_name = message.channel.name.lower()
        if channel_name not in self.channels:
            return

        channel = self.channels[channel_name]
        await channel.handle_message(message)

        if message.content.split(" ", 1)[0][1:] not in self.commands:
            return

        await self.handle_commands(message)

    async def event_raw_usernotice(self, channel: Channel, tags: dict):
        bot_channel = self.channels.get(channel.name.lower())

        if not bot_channel:
            smelly_logger.info("???")

        author_username = tags.get("login")

        if not author_username:
            smelly_logger.info("???")

        await bot_channel.handle_usernotice(author_username, tags)

    async def event_error(self, error: Exception, data: str = None):
        smelly_logger.error(f"{error}: {data}")
        
    async def event_command_error(self, context: Context, error: Exception):
        smelly_logger.error(f"{error}: {context.author}: {context.message}")
