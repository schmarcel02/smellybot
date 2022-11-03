from smellybot.access_control import MasterOnly
from smellybot.bot_command import BotCommand
from smellybot.bot_module import BotModule
from smellybot.config.secure_config import Config
from smellybot.context import MessageContext


class Relay(BotModule):

    def __init__(self, config: Config, bot_channel):
        super().__init__(config, bot_channel)
        self.command_list()

    @classmethod
    def name(cls):
        return "relay"

    def command_list(self):
        self.add_command(BotCommand(Config("relay", self.config), self, self.relay, name="relay", access_control=MasterOnly()))

    async def relay(self, context: MessageContext, arguments: str, _, __, **_kwargs):
        await self.bot_channel.send(arguments)
