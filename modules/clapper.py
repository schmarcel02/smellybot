import random
import re
from datetime import datetime

from twitchio import Message

from config import ModuleConfig
from smellybot import BotModule, BotChannel


class ClapContext:
    DISTINCT_USER_CLAPS_TO_TRIGGER = 3
    CLAP_TIMEOUT_SECONDS = 30
    DISTINCT_USER_FS_TO_TRIGGER = 3
    F_TIMEOUT_SECONDS = 30

    def __init__(self, logger):
        self.logger = logger
        self.clap_users = {}
        self.last_clap = 0.0
        self.f_users = {}
        self.last_f = 0.0

    def clap(self, username):
        current_timestamp = datetime.now().timestamp()
        for u, last_clap in list(self.clap_users.items()):
            if last_clap < current_timestamp - self.CLAP_TIMEOUT_SECONDS:
                del self.clap_users[u]
        self.clap_users[username] = current_timestamp
        number_of_claps = len(self.clap_users)
        self.logger.info("Number of claps: %s", number_of_claps)
        if len(self.clap_users) >= self.DISTINCT_USER_CLAPS_TO_TRIGGER \
                and self.last_clap < current_timestamp - self.CLAP_TIMEOUT_SECONDS:
            self.last_clap = current_timestamp
            return True
        return False

    def f(self, username):
        current_timestamp = datetime.now().timestamp()
        for u, last_f in list(self.f_users.items()):
            if last_f < current_timestamp - self.F_TIMEOUT_SECONDS:
                del self.f_users[u]
        self.f_users[username] = current_timestamp
        number_of_fs = len(self.f_users)
        self.logger.info("Number of Fs: %s", number_of_fs)
        if len(self.f_users) >= self.DISTINCT_USER_FS_TO_TRIGGER \
                and self.last_f < current_timestamp - self.F_TIMEOUT_SECONDS:
            self.last_f = current_timestamp
            return True
        return False


class Clapper(BotModule):
    CLAP_REGEX = re.compile(r".*\b(Clap|clap)\b.*")
    F_REGEX = re.compile(r".*\b([Ff])\b.*")

    def __init__(self, bot_channel: BotChannel, module_config: ModuleConfig):
        super().__init__(bot_channel, module_config)
        self.clap_context: ClapContext = ClapContext(self.logger)
        self.command_list()

    @classmethod
    def name(cls):
        return "clapper"

    def command_list(self):
        self.add_command(self.send_clap, name="applause")
        self.add_command(self.send_f, name="f")

    async def handle_message(self, message: Message):
        if message.author.name.lower() == "smelsbot":
            return

        if self.CLAP_REGEX.match(message.content):
            self.logger.info(f"{message.author.name}: {message.content}")
            clap = self.clap_context.clap(message.author.name.lower())
            if clap:
                await self.send_clap()
            return

        if self.F_REGEX.match(message.content):
            self.logger.info(f"{message.author.name}: {message.content}")
            f = self.clap_context.f(message.author.name.lower())
            if f:
                await self.send_f()
            return

    async def send_clap(self):
        clap_messages = ["Clap", "Clap Clap", "Clap Clap Clap"]
        message = random.choice(clap_messages)
        await self.bot_channel.send(message)

    async def send_f(self):
        await self.bot_channel.send("F")
