import random
import time

from twitchio import Message
from twitchio.ext.commands import Context

from config import ModuleConfig
from smellybot import BotModule, BotChannel, AccessControl


class Sasser(BotModule):
    ROBYN_BOT_NAME = "SaikouRobynBot"

    def __init__(self, bot_channel: BotChannel, module_config: ModuleConfig):
        super().__init__(bot_channel, module_config)
        self.command_list()

    @classmethod
    def name(cls):
        return "sasser"

    def command_list(self):
        self.add_command(self.brb, access_control=AccessControl.MASTER_ONLY)
        self.add_command(self.back, access_control=AccessControl.MASTER_ONLY)

    async def handle_message(self, message: Message):
        pass

    async def brb(self, ctx: Context):
        await self.send_sassy_answer(ctx.author.name)

    async def back(self, ctx: Context):
        await self.send_sassy_answer(ctx.author.name)

    async def send_sassy_answer(self, username: str):
        answers = [
            f"@{username} you can speak for yourself, i'm not @{self.ROBYN_BOT_NAME}, you husk!",
            f"@{username} i'm not your servant, speak for yourself, you husk!",
            f"@{username} tell them yourself, or did you forget how to speak, you husk?"
        ]
        message = random.choice(answers)
        await self.bot_channel.send(message)
