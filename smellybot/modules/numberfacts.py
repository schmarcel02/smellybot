import random

import requests

from smellybot.bot_command import BotCommand
from smellybot.bot_module import BotModule
from smellybot.config.secure_config import Config
from smellybot.context import MessageContext

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

    def __init__(self, config: Config, bot_channel):
        super().__init__(config, bot_channel)
        self.number_api = NumberAPI()
        self.command_list()

    @classmethod
    def name(cls):
        return "numberfacts"

    def command_list(self):
        self.add_command(BotCommand(Config("numberfact", self.config), self, self.numberfact, name="numberfact"))

    async def _handle_usernotice(self, author_username: str, tags: dict):
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
        if self.bot_channel.name.lower() == "nathxn":
            custom_facts = {}
        else:
            custom_facts = {}

        if number_of_months in custom_facts:
            funfact = random.choice(custom_facts[number_of_months])
        else:
            funfact = self.number_api.fact(number_of_months)[:-1]  # Remove last period

        message = f"@{username} Congrats on {number_of_months} months! Did you know that {funfact}?"
        await self.bot_channel.send(message)

    async def numberfact(self, context: MessageContext, arguments: str, __, ___, **_kwargs):
        arguments_split = arguments.split(" ", 1)
        try:
            number = int(arguments_split[0])
        except ValueError:
            self.logger.warning("Invalid number argument provided")
            return
        funfact = self.number_api.fact(number)  # Remove last period
        message = f"@{context.author.display_name} {funfact}"
        await self.bot_channel.send(message)
