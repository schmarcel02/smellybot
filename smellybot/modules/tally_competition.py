import re

import yaml
import math

from smellybot.bot_command import BotCommand
from smellybot.bot_module import BotModule
from smellybot.config.secure_config import Config
from smellybot.access_control import Everyone, ModPlus


class TallyComp(BotModule):
    USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_]+$')
    POINTS_CAP = 30

    def __init__(self, config: Config, bot_channel):
        super().__init__(config, bot_channel)
        self.standings = {}
        self.load_standings()
        self.command_list()

    def load_standings(self):
        self.logger.info("Loading standings...")
        with open("data/standings.yaml", "r+") as standings_file:
            self.standings = yaml.load(standings_file, Loader=yaml.SafeLoader)["standings"]

    def save_standings(self):
        self.logger.info("Saving standings...")
        with open("data/standings.yaml", "w+") as standings_file:
            yaml.dump({"standings": self.standings}, standings_file, Dumper=yaml.SafeDumper)

    @classmethod
    def name(cls):
        return "tallycomp"

    def command_list(self):
        self.add_command(BotCommand(Config("win", self.config), self, self.win, name="win", access_control=ModPlus()))
        self.add_command(BotCommand(Config("wingp", self.config), self, self.wingp, name="wingp", access_control=ModPlus()))
        self.add_command(BotCommand(Config("unwin", self.config), self, self.unwin, name="unwin", access_control=ModPlus()))
        self.add_command(BotCommand(Config("standings", self.config), self, self.standings_table, name="standings", access_control=Everyone()))
        self.add_command(BotCommand(Config("ogstandings", self.config), self, self.og_standings, name="ogstandings", access_control=Everyone()))

    def clean_username(self, username: str):
        return username.strip(" \n\t@").lower()

    def check_username(self, username: str):
        return self.USERNAME_REGEX.fullmatch(username)

    def get_points(self, username: str):
        if username not in self.standings:
            return 0
        return self.standings[username]

    def increment_points(self, username: str, amount: int = 1):
        if username not in self.standings:
            self.standings[username] = 0
        self.standings[username] += amount

    async def standings_table(self, _, _arguments: str, ___, ____, **_kwargs):
        await self.send_standings()

    async def og_standings(self, _, _arguments: str, ___, ____, **_kwargs):
        ordered_standings = sorted(self.standings.items(), key=lambda d: d[1], reverse=True)
        standings_message = " | ".join([f"{k}: {v}" for k, v in ordered_standings if v > 0])
        await self.bot_channel.send(standings_message)

    async def win(self, _, arguments: str, ___, ____, **_kwargs):
        username = self.clean_username(arguments)
        if not self.check_username(username):
            await self.bot_channel.send("Invalid username")
            return

        self.increment_points(username)
        self.save_standings()
        await self.send_standings()

    async def wingp(self, _, arguments: str, ___, ____, **_kwargs):
        username = self.clean_username(arguments)
        if not self.check_username(username):
            await self.bot_channel.send("Invalid username")
            return

        self.increment_points(username)
        self.save_standings()
        await self.send_standings()
        return

    async def unwin(self, _, arguments: str, ___, ____, **_kwargs):
        username = self.clean_username(arguments)
        if not self.check_username(username):
            await self.bot_channel.send("Invalid username")
            return

        self.increment_points(username, -1)
        self.save_standings()
        await self.send_standings()

    async def send_standings(self):
        ordered_standings = sorted(self.standings.items(), key=lambda d: d[1], reverse=True)
        capped_standings = [(k, v if v <= 30 else 30 + math.floor((v-30)/4)) for k, v in ordered_standings if v > 0]
        standings_message = " | ".join([f"{k}: {v}" for k, v in capped_standings if v > 0])
        await self.bot_channel.send(standings_message)
