import yaml

from smellybot.bot_command import BotCommand
from smellybot.bot_module import BotModule
from smellybot.config.secure_config import Config
from smellybot.access_control import Everyone, ModPlus


class TallyComp(BotModule):
    def __init__(self, config: Config, bot_channel):
        super().__init__(config, bot_channel)
        print("init standings")
        self.standings = {}
        self.load_standings()
        self.command_list()

    def load_standings(self):
        with open("data/standings.yaml", "r+") as standings_file:
            self.standings = yaml.load(standings_file, Loader=yaml.SafeLoader)["standings"]

    def save_standings(self):
        with open("data/standings.yaml", "w+") as standings_file:
            yaml.dump({"standings": self.standings}, standings_file, Dumper=yaml.SafeDumper)

    @classmethod
    def name(cls):
        return "tallycomp"

    def command_list(self):
        self.add_command(BotCommand(Config("win", self.config), self, self.win, name="win", access_control=ModPlus()))
        self.add_command(BotCommand(Config("unwin", self.config), self, self.unwin, name="unwin", access_control=ModPlus()))
        self.add_command(BotCommand(Config("standings", self.config), self, self.c_standings, name="standings", access_control=Everyone()))

    async def c_standings(self, _, _arguments: str, ___, ____, **_kwargs):
        await self.send_standings()

    async def win(self, _, arguments: str, ___, ____, **_kwargs):
        print("win", arguments)
        username = arguments.strip()
        username = username.strip("@")
        username = username.lower()
        if " " in username or "@" in username:
            self.bot_channel.send("Invalid username")
        if username not in self.standings:
            self.standings[username] = 0
        self.standings[username] += 1
        if self.standings[username] == 0:
            del self.standings[username]
        self.save_standings()
        await self.send_standings()

    async def unwin(self, _, arguments: str, ___, ____, **_kwargs):
        print("unwin", arguments)
        username = arguments.strip()
        username = username.strip("@")
        username = username.lower()
        if " " in username or "@" in username:
            self.bot_channel.send("Invalid username")
        if username not in self.standings:
            self.standings[username] = 0
        self.standings[username] -= 1
        if self.standings[username] == 0:
            del self.standings[username]
        self.save_standings()
        await self.send_standings()

    async def send_standings(self):
        print("Sending standings")
        ordered_standings = sorted(self.standings.items(), key=lambda d: d[1], reverse=True)
        standings_message = " | ".join([f"{k}: {v}" for k, v in ordered_standings])
        await self.bot_channel.send(standings_message)
