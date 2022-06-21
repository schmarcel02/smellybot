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

    async def relay(self, ctx: Context, arguments: str, _, __):
        if not self.module_config.bot_config.is_master_user(ctx.author.name):
            return

        await self.bot_channel.send(arguments)
