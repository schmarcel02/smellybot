import random

from twitchio import Message
from twitchio.ext.commands import Context

from config import ModuleConfig
from smellybot import BotModule, BotChannel


class Math(BotModule):

    def __init__(self, bot_channel: BotChannel, module_config: ModuleConfig):
        super().__init__(bot_channel, module_config)
        self.command_list()

    @classmethod
    def name(cls):
        return "math"

    def command_list(self):
        self.add_command(self.random)

    async def handle_message(self, message: Message):
        pass

    async def random(self, ctx: Context):
        command_split = ctx.message.content.split(" ", 3)
        if len(command_split) == 0:
            self.logger.warning("No... command provided?")
            return

        lower_bound = 0
        upper_bound = 10

        try:
            if len(command_split) > 1:
                upper_bound = int(command_split[1])

            if len(command_split) > 2:
                lower_bound = int(command_split[1])
                upper_bound = int(command_split[2])
        except ValueError:
            self.logger.warning("Invalid number argument provided")
            return

        await self.send_random_number(lower_bound, upper_bound)

    async def send_random_number(self, lower_bound: int, upper_bound: int):
        random_int = random.randrange(lower_bound, upper_bound+1)
        await self.bot_channel.send(str(random_int))
