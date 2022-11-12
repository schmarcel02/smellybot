import yaml

from smellybot.bot_command import BotCommand
from smellybot.bot_module import BotModule
from smellybot.config.secure_config import Config
from smellybot.context import MessageContext


class Jackbox(BotModule):
    def __init__(self, config: Config, bot_channel):
        super().__init__(config, bot_channel)
        self.command_list()
        self.jackbox_games = {}
        self.load_jackbox_games()

    @classmethod
    def name(cls):
        return "jackbox"

    def command_list(self):
        self.add_command(BotCommand(Config("jackbox", self.config), self, self.jackbox, name="jackbox"))

    def load_jackbox_games(self):
        with open("data/jackbox_games.yaml", "r") as jackbox_games_file:
            games_per_pack = yaml.load(jackbox_games_file, Loader=yaml.SafeLoader)
            self.jackbox_games = {game: pack for pack, games in games_per_pack.items() for game in games}

    async def _handle_message(self, context: MessageContext):
        pass

    async def jackbox(self, _, arguments, __, ___, **_kwargs):
        results = []
        for game, pack in self.jackbox_games.items():
            if arguments.lower() in game.lower():
                results.append((game, pack))

        message = " | ".join([f"'{game}' in {pack}" for game, pack in results])
        await self.bot_channel.send(message)
