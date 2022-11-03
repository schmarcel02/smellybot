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

        print("message:", context.message)
        print("level:", self.level)
        print("length:", length)

        if self.level == 0:
            self.current_emote = message_split[0]
            if length == 1:
                print("advance to level 1")
                self.level = 1
            return

        if message_split[0] != self.current_emote:
            self.current_emote = message_split[0]
            if length == 1:
                print("return to level 1")
                self.level = 1
            else:
                self.level = 0

        if self.level == 1:
            if length == 2:
                if context.author.username == "nathxn":
                    await self.bot_channel.send("Denied Kappa")
                    self.level = 0
                else:
                    print("advance to level 2")
                    self.level = 2
            else:
                self.level = 0
            return

        self.current_emote = message_split[0]

        if self.level == 2:
            if length == 3:
                print("advance to level 3")
                self.level = 3
            else:
                self.level = 0
            return

        if self.level == 3:
            if length == 2:
                if random.random() < 0:
                    print("intervening")
                    await self.intervene()
                    self.level = 0
                elif random.random() < 0:
                    print("helping")
                    await self.help()
                    self.level = 0
                else:
                    print("advance to level 4")
                    self.level = 4
            else:
                self.level = 0
            return

        if self.level == 4:
            if length == 1:
                if random.random() < 1:
                    print("intervening late")
                    await self.intervene_late()
            self.level = 0
            return

    async def help(self):
        await self.bot_channel.send(self.current_emote)


    async def intervene(self):
        interventions = ["Kappa", "*coughs*", "Not Cringe"]
        await self.bot_channel.send(random.choice(interventions))

    async def intervene_late(self):
        interventions = ["I agree, even I, a soulless machine, find this cringe"]
        await self.bot_channel.send(random.choice(interventions))
