from twitchio import Message
from twitchio.ext.commands import Context

import requests

from config import ModuleConfig
from smellybot import BotModule, BotChannel

WOLFRAM_ALPHA_API_BASE_URL = "https://api.wolframalpha.com/v1/"
WOLFRAM_ALPHA_APP_ID = "T6VLJX-Y6A5PW8AEE"


class WolframAlphaAPI:
    def __init__(self):
        pass

    def question(self, query: str):
        url = WOLFRAM_ALPHA_API_BASE_URL + "result"
        response = requests.get(url, params={"i": query, "appid": WOLFRAM_ALPHA_APP_ID})
        if response.status_code != 501:
            response.raise_for_status()
        return response.text


class AskSmel(BotModule):
    def __init__(self, bot_channel: BotChannel, module_config: ModuleConfig):
        super().__init__(bot_channel, module_config)
        self.wolfram_alpha_api = WolframAlphaAPI()
        self.command_list()

    @classmethod
    def name(cls):
        return "asksmel"

    def command_list(self):
        self.add_command(self.jisho, name="asksmel")

    async def handle_message(self, message: Message):
        pass

    async def jisho(self, ctx: Context, query: str, __, ___):
        self.logger.info(f"Querying Wolfram Alpha: {query}")
        result = self.wolfram_alpha_api.question(query)

        if not self.validate_result(result):
            self.logger.warning("Invalid result: %s", result)

        formatted_result = self.format_result(result)
        await self.bot_channel.send(f"{ctx.author.display_name} {formatted_result}")

    def validate_result(self, result: str):
        return True

    def format_result(self, result: dict):
        return result
