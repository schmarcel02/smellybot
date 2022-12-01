import requests
import romkan

from smellybot.bot_command import BotCommand
from smellybot.bot_module import BotModule
from smellybot.config.secure_config import Config
from smellybot.context import MessageContext

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

    def __init__(self, config: Config, bot_channel):
        super().__init__(config, bot_channel)
        self.jisho_api = JishoAPI()
        self.command_list()

    @classmethod
    def name(cls):
        return "jisho"

    def command_list(self):
        self.add_command(BotCommand(Config("jisho", self.config), self, self.jisho, name="jisho", aliases=["kanji"]))

    async def _handle_message(self, context: MessageContext):
        pass

    async def jisho(self, _, query, __, ___, **_kwargs):
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

        romaji = romkan.to_roma(reading)

        return f"{kanji} | {reading} | {romaji} | {definitions}"
