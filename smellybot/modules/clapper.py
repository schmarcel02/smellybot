import random
import re
from datetime import datetime

from smellybot.bot_command import BotCommand
from smellybot.bot_module import BotModule
from smellybot.config.definition import ConfigDefinition
from smellybot.config.secure_config import Config
from smellybot.config.types.int import CInt
from smellybot.context import MessageContext


class ClapContext:
    def __init__(self, config: Config, logger):
        self.claps_to_trigger = config.register(ConfigDefinition("clapper.claps_to_trigger", ctype=CInt()))
        self.clap_timeout = config.register(ConfigDefinition("clapper.clap_timeout", ctype=CInt()))
        self.clap_timeframe = config.register(ConfigDefinition("clapper.clap_timeframe", ctype=CInt()))

        self.logger = logger
        self.clap_users = {}
        self.last_clap = 0.0
        self.f_users = {}
        self.last_f = 0.0

    def clap(self, username):
        current_timestamp = datetime.now().timestamp()
        for u, last_clap in list(self.clap_users.items()):
            if last_clap < current_timestamp - self.clap_timeframe.get():
                del self.clap_users[u]
        self.clap_users[username] = current_timestamp
        number_of_claps = len(self.clap_users)
        self.logger.info("Number of claps: %s", number_of_claps)
        if len(self.clap_users) >= self.claps_to_trigger.get() \
                and self.last_clap < current_timestamp - self.clap_timeout.get():
            self.last_clap = current_timestamp
            self.clap_users.clear()
            return True
        return False

    def f(self, username):
        current_timestamp = datetime.now().timestamp()
        for u, last_f in list(self.f_users.items()):
            if last_f < current_timestamp - self.clap_timeframe.get():
                del self.f_users[u]
        self.f_users[username] = current_timestamp
        number_of_fs = len(self.f_users)
        self.logger.info("Number of Fs: %s", number_of_fs)
        if len(self.f_users) >= self.claps_to_trigger.get() \
                and self.last_f < current_timestamp - self.clap_timeout.get():
            self.last_f = current_timestamp
            self.f_users.clear()
            return True
        return False


class Clapper(BotModule):
    CLAP_REGEX = re.compile(r"\b(Clap|clap)\b")
    F_REGEX = re.compile(r"\b([Ff])\b")

    def __init__(self, config: Config, bot_channel):
        super().__init__(config, bot_channel)
        self.clap_context: ClapContext = ClapContext(config, self.logger)
        self.command_list()

    @classmethod
    def name(cls):
        return "clapper"

    def command_list(self):
        self.add_command(BotCommand(Config("clap", self.config), self, self.clap, name="clap", aliases=["applause"]))
        self.add_command(BotCommand(Config("f", self.config), self, self.f, name="f"))

    async def _handle_message(self, context: MessageContext):
        if context.author.username.lower() == "smelsbot":
            return

        if self.CLAP_REGEX.search(context.message):
            self.logger.info(f"{context.author.username}: {context.message}")
            clap = self.clap_context.clap(context.author.username.lower())
            if clap:
                await self.send_clap()
            return

        if self.F_REGEX.search(context.message):
            self.logger.info(f"{context.author.username}: {context.message}")
            f = self.clap_context.f(context.author.username.lower())
            if f:
                await self.send_f()
            return

    async def f(self, _, __, ___, ____, **_kwargs):
        await self.send_f()

    async def clap(self, _, arguments: str, ___, ____, **_kwargs):
        arguments_split = arguments.split(" ", 1)

        try:
            number_of_claps = int(arguments_split[0])
        except IndexError:
            number_of_claps = None
        except ValueError:
            self.logger.warning("Invalid int argument provided")
            return

        if number_of_claps > 20:
            self.logger.warning("Provided number too big")
            return

        await self.send_clap(number_of_claps)

    async def send_clap(self, number_of_claps: int = None):
        number_of_claps = number_of_claps or random.randrange(1, 4)
        message = "Clap " * number_of_claps
        await self.bot_channel.send(message.strip())

    async def send_f(self):
        await self.bot_channel.send("F")
