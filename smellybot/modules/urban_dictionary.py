
import requests
from math import sqrt

from smellybot.bot_command import BotCommand
from smellybot.bot_module import BotModule
from smellybot.config.secure_config import Config
from smellybot.context import MessageContext

UD_API_BASE_URL = "https://mashape-community-urban-dictionary.p.rapidapi.com/"
UD_API_HEADERS = {
    'X-RapidAPI-Key': '4adceaf68bmsh7154ee14132b931p1d34a4jsn581e2872c0b5',
    'X-RapidAPI-Host': 'mashape-community-urban-dictionary.p.rapidapi.com'
}


def confidence(ups, downs):
    n = ups + downs

    if n == 0:
        return 0

    z = 1.0 #1.44 = 85%, 1.96 = 95%
    phat = float(ups) / n
    return ((phat + z*z/(2*n) - z * sqrt((phat*(1-phat)+z*z/(4*n))/n))/(1+z*z/n))


class UDAPI:
    def __init__(self):
        pass

    def search(self, keyword: str):
        url = UD_API_BASE_URL + "define"
        response = requests.get(url, params={"term": keyword}, headers=UD_API_HEADERS)
        response.raise_for_status()
        return response.json()


class UrbanDictionary(BotModule):
    def __init__(self, config: Config, bot_channel):
        super().__init__(config, bot_channel)
        self.ud_api = UDAPI()
        self.command_list()

    @classmethod
    def name(cls):
        return "urbandictionary"

    def command_list(self):
        self.add_command(BotCommand(Config("jisho", self.config), self, self.ud, name="ud", aliases=["urban", "urbandictionary"]))

    async def _handle_message(self, context: MessageContext):
        pass

    async def ud(self, _, query, __, ___, **_kwargs):
        result = self.ud_api.search(query)
        formatted_result = self.format_result(result)
        await self.bot_channel.send(formatted_result or "No Result")

    def validate_result(self, result: dict):
        if len(result["list"] == 0):
            return False
        return True

    def format_result(self, result: dict):
        definitions = result["list"]

        max_confidence = 0
        max_definition = None

        for definition in definitions:
            conf = confidence(definition["thumbs_up"], definition["thumbs_down"])
            if conf > max_confidence:
                max_confidence = conf
                max_definition = definition

        if max_definition:
            return max_definition["definition"][:480]
        return None
