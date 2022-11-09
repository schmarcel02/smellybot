from typing import cast

from smellybot.bot_module import BotModule
from smellybot.config.definition import ListConfigDefinition
from smellybot.config.element import ListConfigElement
from smellybot.config.secure_config import Config
from smellybot.config.types.string import CString
from smellybot.context import MessageContext


class Switcher(BotModule):

    def __init__(self, config: Config, bot_channel):
        self.keywords = cast(ListConfigElement, config.register(ListConfigDefinition("switcher.keywords", ctype=CString())))
        super().__init__(config, bot_channel)

    @classmethod
    def name(cls):
        return "switcher"

    async def _handle_message(self, context: MessageContext):
        if context.author.has_role("sub"):
            return

        for keyword in self.keywords.get():
            if context.message == keyword:
                await self.send_switch_command()

    async def send_switch_command(self):
        await self.bot_channel.send("!switch")
