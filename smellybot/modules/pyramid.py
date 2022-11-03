import random

from smellybot.bot_module import BotModule
from smellybot.config.secure_config import Config
from smellybot.context import MessageContext


class Pyramid(BotModule):

    def __init__(self, config: Config, bot_channel):
        super().__init__(config, bot_channel)
        self.level = 0
        self.current_emote = ""

    @classmethod
    def name(cls):
        return "pyramid"

    async def _handle_message(self, context: MessageContext):
        message_split = context.message.split(" ")

        length = len(message_split)

        for i in range(1, len(message_split)):
            if message_split[i - 1] != message_split[i]:
                self.level = 0
                return

        if self.level == 0:
            if length == 1:
                self.level = 1
            return

        if message_split[0] != self.current_emote:
            self.current_emote = message_split[0]
            if length == 1:
                self.level = 1
            else:
                self.level = 0

        if self.level == 1:
            if length == 2:
                self.level = 2
            else:
                self.level = 0
            return

        self.current_emote = message_split[0]

        if self.level == 2:
            if length == 3:
                self.level = 3
            else:
                self.level = 0
            return

        if self.level == 3:
            if length == 2:
                await self.send_emote()
            else:
                self.level = 0
            return

    async def send_emote(self):
        if random.random() < 0.5:
            await self.bot_channel.send("mudantIssapointed")
        else:
            await self.bot_channel.send(self.current_emote)
