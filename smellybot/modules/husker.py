import random
import re
from typing import cast

from smellybot.bot_module import BotModule
from smellybot.config.definition import ListConfigDefinition, ConfigDefinition
from smellybot.config.element import ListConfigElement
from smellybot.config.secure_config import Config
from smellybot.config.types.string import CUsername, CString
from smellybot.context import MessageContext


class Husker(BotModule):
    SCUFF_BOT_NAME = "huskorhusk"
    SCUFF_REGEX = re.compile(r"^Thanks @(?P<caller_name>[^\s]+) The Stream Scuff Level is currently (?P<scuff_level>[\d.]+)$")

    def __init__(self, config: Config, bot_channel):
        self.scuff_bot_names = cast(ListConfigElement, config.register(ListConfigDefinition("husker.scuff_bot_names", ctype=CUsername())))
        self.scuff_regex = config.register(ConfigDefinition("husker.scuff_regex", ctype=CString()))
        super().__init__(config, bot_channel)

    @classmethod
    def name(cls):
        return "husker"

    async def _handle_message(self, context: MessageContext):
        if context.author.username.lower() not in self.scuff_bot_names.get():
            return
        scuff_match = self.SCUFF_REGEX.match(context.message)
        if scuff_match:
            capture_groups = scuff_match.groupdict()
            caller_name = capture_groups.get("caller_name", "unknown")
            scuff_level = float(capture_groups["scuff_level"])

            self.logger.info(f"{context.author.username}: {context.message}")
            await self.scuff(context.author.display_name, caller_name, scuff_level)
            return

    async def scuff(self, scuff_bot_name: str, caller_name: str, scuff_level: float):
        if scuff_level < 3:
            await self.send_low_scuff_level_answer(scuff_bot_name, caller_name, scuff_level)

    async def send_low_scuff_level_answer(self, scuff_bot_name: str, caller_name: str, scuff_level: float):
        answers = [
            f"Only {scuff_level:.1f}? That can't be right... Check your sensors @{scuff_bot_name}",
            f"@{scuff_bot_name} you accidentally added a dot, you probably meant {int(scuff_level*10.0)}",
            f"@{scuff_bot_name} i think you're missing a few 0s there"
        ]
        message = random.choice(answers)
        await self.bot_channel.send(message)
