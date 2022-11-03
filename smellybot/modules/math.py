import random

from smellybot.bot_command import BotCommand
from smellybot.bot_module import BotModule
from smellybot.config.secure_config import Config
from smellybot.context import MessageContext


class Math(BotModule):

    def __init__(self, config: Config, bot_channel):
        super().__init__(config, bot_channel)
        self.command_list()

    @classmethod
    def name(cls):
        return "math"

    def command_list(self):
        self.add_command(BotCommand(Config("random", self.config), self, self.random, name="random"))

    async def _handle_message(self, context: MessageContext):
        pass

    async def random(self, _, arguments: str, __, ___, **_kwargs):
        arguments_split = arguments.split(" ", 2)

        lower_bound = 0
        upper_bound = 10

        try:
            if len(arguments_split) > 0:
                upper_bound = int(arguments_split[0])

            if len(arguments_split) > 1:
                lower_bound = int(arguments_split[0])
                upper_bound = int(arguments_split[1])
        except ValueError:
            self.logger.warning("Invalid number argument provided")
            return

        await self.send_random_number(lower_bound, upper_bound)

    async def send_random_number(self, lower_bound: int, upper_bound: int):
        random_int = random.randrange(lower_bound, upper_bound+1)
        await self.bot_channel.send(str(random_int))
