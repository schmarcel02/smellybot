import random
import re

from twitchio import Message

from config import ModuleConfig
from smellybot import BotModule, BotChannel


class Husker(BotModule):
    SCUFF_BOT_NAME = "huskorhusk"
    SCUFF_REGEX = re.compile(r"^Thanks @[^\s]+ The Stream Scuff Level is currently ([\d\.]+)$")

    def __init__(self, bot_channel: BotChannel, module_config: ModuleConfig):
        super().__init__(bot_channel, module_config)

    @classmethod
    def name(cls):
        return "husker"

    async def handle_message(self, message: Message):
        if message.author.name.lower() == self.SCUFF_BOT_NAME.lower():
            scuff_match = self.SCUFF_REGEX.match(message.content)
            if scuff_match:
                self.logger.info(f"{message.author.name}: {message.content}")
                scuff_level = float(scuff_match[1])
                await self.scuff(scuff_level)
                return

    async def scuff(self, scuff_level: float):
        if scuff_level < 3:
            await self.send_low_scuff_level_answer(scuff_level)

    async def send_low_scuff_level_answer(self, scuff_level: float):
        answers = [
            f"Only {scuff_level:.1f}? That can't be right... Check your sensors @{self.SCUFF_BOT_NAME}",
            f"@{self.SCUFF_BOT_NAME} you accidentally added a dot, you probably meant {int(scuff_level*10.0)}",
            f"@{self.SCUFF_BOT_NAME} i think you're missing a few 0s there"
        ]
        message = random.choice(answers)
        await self.bot_channel.send(message)
