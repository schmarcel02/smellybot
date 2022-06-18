from typing import Type

from twitchio import Message
from twitchio.ext.commands import Context

from config import ModuleConfig
from smellybot import BotModule, BotChannel, AccessControl


class Controller(BotModule):
    def __init__(self, bot_channel: BotChannel, module_config: ModuleConfig):
        super().__init__(bot_channel, module_config)
        self.command_list()

    @classmethod
    def name(cls):
        return "controller"

    def command_list(self):
        self.add_command(self.smellybot, access_control=AccessControl.MOD_PLUS)

    async def handle_message(self, message: Message):
        pass

    async def smellybot(self, ctx: Context):
        message = ctx.message.content
        command_split = message.split(" ", 2)

        if len(command_split) == 0:
            self.logger.warning("No... command provided?")
            return
        if len(command_split) == 1:
            self.logger.warning("No subcommand provided")
            return

        subcommand = command_split[1]

        if subcommand == "enable":
            await self.sub_set_active(ctx, True)
        elif subcommand == "disable":
            await self.sub_set_active(ctx, False)
        elif subcommand == "addadmin":
            await self.sub_add_admin(ctx)
        elif subcommand == "remadmin":
            await self.sub_remove_admin(ctx)
        elif subcommand == "addmod":
            await self.sub_add_mod(ctx)
        elif subcommand == "remmod":
            await self.sub_remove_mod(ctx)
        elif subcommand == "shutdown":
            await self.sub_shutdown(ctx)
        elif subcommand == "addchannel":
            await self.sub_add_channel(ctx)

    async def sub_set_active(self, ctx: Context, active: bool):
        command_split = ctx.message.content.split(" ")
        if not self.module_config.bot_config.is_master_user(ctx.author.name) \
                and not ctx.author.name.lower() == self.bot_channel.channel_name.lower() \
                and not self.bot_channel.channel_config.is_mod_user(ctx.author.name) \
                and not self.module_config.bot_config.is_admin_user(ctx.author.name):
            self.logger.warning("User '%s' is not authorized to use subcommand '%s'", ctx.author.name, command_split[1])
            return
        if len(command_split) < 3:
            await self.bot_channel.activate() if active else await self.bot_channel.deactivate()
            return
        if len(command_split) == 3:
            module_name = command_split[2].lower()
            module = self.bot_channel.modules.get(module_name)
            if not module:
                self.logger.warning("Module '%s' not found", module_name)
                return
            await module.activate() if active else await module.deactivate()
            return
        if len(command_split) >= 4:
            module_name = command_split[2].lower()
            command_name = command_split[3].lower()
            module = self.bot_channel.modules.get(module_name)
            if not module:
                self.logger.warning("Module '%s' not found", module_name)
                return
            command = module.commands.get(command_name)
            if not command:
                self.logger.warning("Command '%s' not found in module '%s'", command_name, module_name)
                return
            await command.activate() if active else await command.deactivate()
            return

    async def sub_add_admin(self, ctx: Context):
        command_split = ctx.message.content.split(" ")
        if not self.module_config.bot_config.is_master_user(ctx.author.name):
            self.logger.warning("User '%s' is not authorized to use subcommand '%s'", ctx.author.name, command_split[1])
            return
        if len(command_split) < 3:
            self.logger.warning("No username provided")
            return
        username = command_split[2]
        self.module_config.bot_config.add_admin_user(username.lower())

    async def sub_remove_admin(self, ctx: Context):
        command_split = ctx.message.content.split(" ")
        if not self.module_config.bot_config.is_master_user(ctx.author.name):
            self.logger.warning("User '%s' is not authorized to use subcommand '%s'", ctx.author.name, command_split[1])
            return
        if len(command_split) < 3:
            self.logger.warning("No username provided")
            return
        username = command_split[2]
        self.module_config.bot_config.remove_admin_user(username.lower())

    async def sub_add_mod(self, ctx: Context):
        command_split = ctx.message.content.split(" ")
        if not self.module_config.bot_config.is_master_user(ctx.author.name) \
                and not ctx.author.name.lower() == self.bot_channel.channel_name.lower() \
                and not self.module_config.bot_config.is_admin_user(ctx.author.name):
            self.logger.warning("User '%s' is not authorized to use subcommand '%s'", ctx.author.name, command_split[1])
            return
        if len(command_split) < 3:
            self.logger.warning("No username provided")
            return
        username = command_split[2]
        self.module_config.add_mod_user(username.lower())

    async def sub_remove_mod(self, ctx: Context):
        command_split = ctx.message.content.split(" ")
        if not self.module_config.bot_config.is_master_user(ctx.author.name) \
                and not ctx.author.name.lower() == self.bot_channel.channel_name.lower() \
                and not self.module_config.bot_config.is_admin_user(ctx.author.name):
            self.logger.warning("User '%s' is not authorized to use subcommand '%s'", ctx.author.name, command_split[1])
            return
        if len(command_split) < 3:
            self.logger.warning("No username provided")
            return
        username = command_split[2]
        self.module_config.remove_mod_user(username.lower())

    async def sub_shutdown(self, ctx: Context):
        command_split = ctx.message.content.split(" ")
        if not self.module_config.bot_config.is_master_user(ctx.author.name) \
                and not self.module_config.bot_config.is_admin_user(ctx.author.name):
            self.logger.warning("User '%s' is not authorized to use subcommand '%s'", ctx.author.name, command_split[1])
            return
        exit(0)

    async def sub_add_channel(self, ctx: Context):
        command_split = ctx.message.content.split(" ")
        if not self.module_config.bot_config.is_master_user(ctx.author.name) \
                and not self.module_config.bot_config.is_admin_user(ctx.author.name):
            self.logger.warning("User '%s' is not authorized to use subcommand '%s'", ctx.author.name, command_split[1])
            return
        if len(command_split) < 3:
            self.logger.warning("No channel provided")
            return

        channel_name = command_split[2]

        if channel_name.lower() in self.bot_channel.smelly_bot.channels:
            self.logger.warning("Channel '%s' was already added", channel_name)

        channel_config = self.module_config.bot_config.get_channel(channel_name)
        bot_channel = BotChannel(self.bot_channel.smelly_bot, channel_config)
        channel_config.get_module("controller").set_enabled(True)
        self.bot_channel.smelly_bot.add_bot_channel(bot_channel)
