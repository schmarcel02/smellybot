from twitchio import Message
from twitchio.ext.commands import Context

import requests

from config import ModuleConfig
from smellybot import BotModule, BotChannel

JISHO_API_BASE_URL = "https://jisho.org/api/v1/"


class JishoAPI:
    def __init__(self):
        pass

    def search(self, keyword: str):
        url = JISHO_API_BASE_URL + "search/words"
        response = requests.get(url, params={"keyword": keyword})
        response.raise_for_status()
        return response.json()


class Jisho(BotModule):
    MASTER_NAME = "SchMarcEL"

    def __init__(self, bot_channel: BotChannel, module_config: ModuleConfig):
        super().__init__(bot_channel, module_config)
        self.jisho_api = JishoAPI()
        self.command_list()

    @classmethod
    def name(cls):
        return "jisho"

    def command_list(self):
        self.add_command(self.jisho, name="jisho", aliases=["kanji"])

    async def handle_message(self, message: Message):
        pass

    async def jisho(self, _, query, __, ___):
        result = self.jisho_api.search(query)
        formatted_result = self.format_result(result)
        await self.bot_channel.send(formatted_result)

    def validate_result(self, result: dict):
        if len(result["data"] == 0):
            return False
        return True

    def format_result(self, result: dict):
        kanji = result["data"][0]["japanese"][0]["word"]
        reading = result["data"][0]["japanese"][0]["reading"]
        definitions = ", ".join(result["data"][0]["senses"][0]["english_definitions"])

        return f"{kanji} | {reading} | {definitions}"
