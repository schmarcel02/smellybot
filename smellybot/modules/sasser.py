import random

from smellybot.access_control import MasterOnly
from smellybot.bot_command import BotCommand
from smellybot.bot_module import BotModule
from smellybot.config.secure_config import Config
from smellybot.context import MessageContext


class Sasser(BotModule):
    ROBYN_BOT_NAME = "SaikouRobynBot"

    def __init__(self, config: Config, bot_channel):
        super().__init__(config, bot_channel)
        self.command_list()

    @classmethod
    def name(cls):
        return "sasser"

    def command_list(self):
        self.add_command(BotCommand(Config("brb", self.config), self, self.brb, name="brb", access_control=MasterOnly()))
        self.add_command(BotCommand(Config("back", self.config), self, self.back, name="back", access_control=MasterOnly()))
        self.add_command(BotCommand(Config("bingchilling", self.config), self, self.bingchilling, name="🍦", access_control=MasterOnly()))

    async def _handle_message(self, context: MessageContext):
        pass

    async def brb(self, context: MessageContext, _, __, ___, **_kwargs):
        await self.send_sassy_answer(context.author.display_name)

    async def back(self, context: MessageContext, _, __, ___, **_kwargs):
        await self.send_sassy_answer(context.author.display_name)

    async def bingchilling(self, context: MessageContext, _, __, ___, **_kwargs):
        await self.bot_channel.send("早上好中国 现在我有冰淇淋🍦我很喜欢冰淇淋🍦但是 速度与激情9 比冰淇淋 🍦度与激情 速度与激情9 我最喜欢 所以…")

    async def send_sassy_answer(self, username: str):
        answers = [
            f"@{username} you can speak for yourself, i'm not @{self.ROBYN_BOT_NAME}, you husk!",
            f"@{username} i'm not your servant, speak for yourself, you husk!",
            f"@{username} tell them yourself, or did you forget how to speak, you husk?"
        ]
        message = random.choice(answers)
        await self.bot_channel.send(message)
