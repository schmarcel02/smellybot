import random

from smellybot.bot_module import BotModule
from smellybot.config.secure_config import Config
from smellybot.config.definition import ConfigDefinition
from smellybot.config.types.int import CInt
from smellybot.context import MessageContext


class Pyramid(BotModule):

    def __init__(self, config: Config, bot_channel):
        super().__init__(config, bot_channel)

        self.chance_to_intervene = config.register(ConfigDefinition("pyramid.chance_to_intervene", ctype=CInt()))
        self.chance_to_help = config.register(ConfigDefinition("pyramid.chance_to_help", ctype=CInt()))

        self.length = 0
        self.past_peak = False
        self.emote = None

    @classmethod
    def name(cls):
        return "pyramid"

    async def _handle_message(self, context: MessageContext):
        message_split = context.message.split(" ")

        length = len(message_split)

        for i in range(1, length):
            if message_split[i - 1] != message_split[i]:
                self.reset()
                return

        emote = message_split[0]

        if emote != self.emote:
            self.reset(emote, length)
            return

        chance_to_intervene = self.chance_to_intervene.get() / 100
        chance_to_help = chance_to_intervene + self.chance_to_help.get() / 100

        if not self.past_peak:
            if length == self.length + 1:
                self.advance(length)
                return
            elif length == self.length - 1:
                if length == 1:
                    self.reset(emote, 1)
                    return
                elif length == 2:
                    rand = random.random()
                    if rand < chance_to_intervene:
                        await self.intervene()
                        self.reset()
                    elif rand < chance_to_help:
                        await self.help()
                        self.reset(emote, 1)
                    else:
                        self.advance(length)
                    return
                else:
                    self.past_peak = True
                    self.advance(length)
                    return


        if length != self.length - 1:
            self.reset(length)
            return

        if length == 2:
            rand = random.random()
            if rand < chance_to_intervene:
                await self.intervene()
                self.reset()
            elif rand < chance_to_help:
                await self.help()
                self.reset(emote, 1)
            else:
                self.advance(length)
            return

        if length == 1:
            self.reset(emote, 1)
            return

    def reset(self, emote: str = None, length: int = 0):
        if self.length > 1:
            self.logger.info("Resetting...")
        self.past_peak = False
        if emote is not None and length == 1:
            self.length = 1
            self.emote = emote
        else:
            self.length = 0
            self.emote = None

    def advance(self, length: int):
        self.length = length
        if self.past_peak or length > 1:
            self.logger.info(f"Pyramid length {length}")

    async def help(self):
        self.logger.info(f"helping with emote: {self.emote}")
        await self.bot_channel.send(self.emote)

    async def intervene(self):
        self.logger.info("intervening")
        interventions = ["Kappa", "No", "JoyAsteroid", "Denied"]
        intervention = random.choice(interventions)
        await self.bot_channel.send(intervention)
        if " " not in intervention:
            self.reset(intervention, 1)
        else:
            self.reset()

    async def intervene_late(self):
        self.logger.info("intervening late")
        interventions = ["I agree. Even I, a soulless machine, find this cringe"]
        await self.bot_channel.send(random.choice(interventions))
