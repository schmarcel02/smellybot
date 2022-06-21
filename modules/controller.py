from twitchio import Message

from config import ModuleConfig
from smellybot import BotModule, BotChannel, AccessControl, SuperCommand, BotCommand


class Controller(BotModule):
    def __init__(self, bot_channel: BotChannel, module_config: ModuleConfig):
        super().__init__(bot_channel, module_config)
        self.command_list()

    @classmethod
    def name(cls):
        return "controller"

    def command_list(self):
        smellybot_command = SuperCommand(self, AccessControl.MOD_PLUS, name="smellybot")
        smellybot_command.add_subcommand(BotCommand(self, self.enable, AccessControl.MOD_PLUS, name="enable"))
        smellybot_command.add_subcommand(BotCommand(self, self.disable, AccessControl.MOD_PLUS, name="disable"))
        smellybot_command.add_subcommand(BotCommand(self, self.add_admin, AccessControl.MASTER_ONLY, name="addadmin"))
        smellybot_command.add_subcommand(BotCommand(self, self.remove_admin, AccessControl.MASTER_ONLY, name="remadmin"))
        smellybot_command.add_subcommand(BotCommand(self, self.add_mod, AccessControl.STREAMER_PLUS, name="addmod"))
        smellybot_command.add_subcommand(BotCommand(self, self.remove_mod, AccessControl.STREAMER_PLUS, name="remmod"))
        smellybot_command.add_subcommand(BotCommand(self, self.shutdown, AccessControl.ADMIN_PLUS, name="shutdown"))
        smellybot_command.add_subcommand(BotCommand(self, self.add_channel, AccessControl.ADMIN_PLUS, name="addchannel"))
        self.add_command_object(smellybot_command)

    async def handle_message(self, message: Message):
        pass

    async def enable(self, _, arguments, __, ___):
        await self.set_active(arguments, True)

    async def disable(self, _, arguments, __, ___):
        await self.set_active(arguments, False)

    async def set_active(self, arguments: str, active: bool):
        if not arguments:
            await self.bot_channel.activate() if active else await self.bot_channel.deactivate()
            return

        arguments_split = arguments.split(" ")

        try:
            module_name = arguments_split[0]
        except IndexError:
            await self.bot_channel.activate() if active else await self.bot_channel.deactivate()
            return

        module = self.bot_channel.modules.get(module_name)
        if not module:
            self.logger.warning(f"Module '{module_name}' not found")
            await self.bot_channel.send(f"Module '{module_name}' not found")
            return

        try:
            command_name = arguments_split[1]
        except IndexError:
            await module.activate() if active else await module.deactivate()
            return

        command = module.commands.get(command_name)
        if not command:
            self.logger.warning(f"Command '{command_name}' not found")
            await self.bot_channel.send(f"Command '{command_name}' not found")
            return

        await command.activate() if active else await command.deactivate()

    async def add_admin(self, _, arguments: str, __, head: str):
        arguments_split = arguments.split(" ")

        try:
            username = arguments_split[0]
        except IndexError:
            self.logger.warning("No username provided")
            await self.bot_channel.send(f"Usage: {head} {{username}}")
            return

        self.module_config.bot_config.add_admin_user(username)
        self.logger.info(f"Added '{username}' to list of admins")
        await self.bot_channel.send(f"User '{username}' can now change settings of bot '{self.module_config.bot_config.get_bot_username()}' for all channels")

    async def remove_admin(self, _, arguments: str, __, head: str):
        arguments_split = arguments.split(" ")

        try:
            username = arguments_split[0]
        except IndexError:
            self.logger.warning("No username provided")
            await self.bot_channel.send(f"Usage: {head} {{username}}")
            return

        self.module_config.bot_config.remove_admin_user(username)
        self.logger.info(f"Removed '{username}' from list of admins")
        await self.bot_channel.send(f"User '{username}' is no longer an admin for bot '{self.module_config.bot_config.get_bot_username()}'")

    async def add_mod(self, _, arguments: str, __, head: str):
        arguments_split = arguments.split(" ")

        try:
            username = arguments_split[0]
        except IndexError:
            self.logger.warning("No username provided")
            await self.bot_channel.send(f"Usage: {head} {{username}}")
            return

        self.module_config.channel_config.add_mod_user(username)
        self.logger.info(f"Added '{username}' to list of mods")
        await self.bot_channel.send(f"User '{username}' can now change settings of bot '{self.module_config.bot_config.get_bot_username()}' for this channel")

    async def remove_mod(self, _, arguments: str, __, head: str):
        arguments_split = arguments.split(" ")

        try:
            username = arguments_split[0]
        except IndexError:
            self.logger.warning("No username provided")
            await self.bot_channel.send(f"Usage: {head} {{username}}")
            return

        self.module_config.channel_config.remove_mod_user(username)
        self.logger.info(f"Removed '{username}' from list of mods")
        await self.bot_channel.send(f"User '{username}' is no longer a mod for bot '{self.module_config.bot_config.get_bot_username()}'")

    async def shutdown(self, _, __, ___, ____):
        exit(0)

    async def add_channel(self, _, arguments: str, __, head: str):
        arguments_split = arguments.split(" ")

        try:
            channel_name = arguments_split[0]
        except IndexError:
            self.logger.warning("No channel name provided")
            await self.bot_channel.send(f"Usage: {head} {{channel name}}")
            return

        if channel_name.lower() in self.bot_channel.smelly_bot.channels:
            self.logger.warning("Channel '%s' was already added", channel_name)
            return

        channel_config = self.module_config.bot_config.get_channel(channel_name)
        bot_channel = BotChannel(self.bot_channel.smelly_bot, channel_config)
        channel_config.get_module("controller").set_enabled(True)
        self.bot_channel.smelly_bot.add_bot_channel(bot_channel)
