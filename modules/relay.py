from twitchio import Message
from twitchio.ext.commands import Context

from config import ModuleConfig
from smellybot import BotModule, BotChannel, AccessControl


class Relay(BotModule):
    def __init__(self, bot_channel: BotChannel, module_config: ModuleConfig):
        super().__init__(bot_channel, module_config)
        self.command_list()

    @classmethod
    def name(cls):
        return "relay"

    def command_list(self):
        self.add_command(self.relay, access_control=AccessControl.ADMIN_PLUS)

    async def handle_message(self, message: Message):
        pass

    async def relay(self, ctx: Context):
        if not self.module_config.bot_config.is_master_user(ctx.author.name):
            return

        command_split = ctx.message.content.split(" ", 1)

        await self.bot_channel.send(command_split[1])
