import requests
from twitchio import Message
from twitchio.ext.commands import Context

from config import ModuleConfig
from smellybot import BotModule, BotChannel

NUMBER_API_BASE_URL = "http://numbersapi.com/"


class NumberAPI:
    def __init__(self):
        pass

    def fact(self, number: int):
        url = NUMBER_API_BASE_URL + str(number)
        response = requests.get(url)
        response.raise_for_status()
        return response.text


class NumberFacts(BotModule):

    def __init__(self, bot_channel: BotChannel, module_config: ModuleConfig):
        super().__init__(bot_channel, module_config)
        self.number_api = NumberAPI()
        self.command_list()

    @classmethod
    def name(cls):
        return "numberfacts"

    def command_list(self):
        self.add_command(self.numberfact, name="numberfact")

    async def handle_message(self, message: Message):
        if "msg-id" in message.tags and message.tags["msg-id"] == "resub":
            self.logger.info(f"{message.author.name}: {message.content}")
            try:
                number_of_months = int(message.tags["msg-param-months"])
            except ValueError:
                self.logger.warning("Invalid value for number of months: %s", message.tags["msg-param-months"])
                return
            await self.send_funfact(message.author.display_name, number_of_months)
        pass

    async def handle_usernotice(self, author_username: str, tags: dict):
        if "msg-id" in tags and tags["msg-id"] == "resub":
            if "msg-param-cumulative-months" not in tags:
                self.logger.warning("Number of months missing in tags")
                return
            try:
                number_of_months = int(tags["msg-param-cumulative-months"])
            except ValueError:
                self.logger.warning("Invalid value for number of months: %s", tags["msg-param-months"])
                return
            self.logger.info(f"{author_username} subbed for {number_of_months} months")

            if number_of_months < 2:
                self.logger.warning("Number of months too low: %s", number_of_months)
                return

            await self.send_funfact(author_username, number_of_months)
        pass

    async def send_funfact(self, username: str, number_of_months: int):
        funfact = self.number_api.fact(number_of_months)[:-1]  # Remove last period
        message = f"@{username} Congrats on {number_of_months} months! Did you know that {funfact}?"
        await self.bot_channel.send(message)

    async def numberfact(self, ctx: Context, arguments: str, __, ___):
        arguments_split = arguments.split(" ", 1)
        try:
            number = int(arguments_split[0])
        except ValueError:
            self.logger.warning("Invalid number argument provided")
            return
        funfact = self.number_api.fact(number)  # Remove last period
        message = f"@{ctx.author.display_name} {funfact}"
        await self.bot_channel.send(message)
