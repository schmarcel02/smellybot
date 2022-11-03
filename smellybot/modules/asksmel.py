import requests

from smellybot.bot_command import BotCommand
from smellybot.bot_module import BotModule
from smellybot.config.secure_config import Config
from smellybot.context import MessageContext

WOLFRAM_ALPHA_API_BASE_URL = "https://api.wolframalpha.com/v1/"
WOLFRAM_ALPHA_APP_ID = "T6VLJX-Y6A5PW8AEE"


class WolframAlphaAPI:
    def __init__(self):
        pass

    def question(self, query: str):
        url = WOLFRAM_ALPHA_API_BASE_URL + "result"
        response = requests.get(url, params={"i": query, "appid": WOLFRAM_ALPHA_APP_ID, "units": "metric"})
        if response.status_code != 501:
            response.raise_for_status()
        return response.text


class AskSmel(BotModule):

    def __init__(self, config: Config, bot_channel):
        super().__init__(config, bot_channel)
        self.wolfram_alpha_api = WolframAlphaAPI()
        self.command_list()

    @classmethod
    def name(cls):
        return "asksmel"

    def command_list(self):
        self.add_command(BotCommand(Config("asksmel", self.config), self, self.asksmel, name="asksmel"))

    async def _handle_message(self, context: MessageContext):
        pass

    async def asksmel(self, context: MessageContext, query: str, __, ___, **_kwargs):
        self.logger.info(f"Querying Wolfram Alpha: {query}")
        result = self.wolfram_alpha_api.question(query)

        if not self.validate_result(result):
            self.logger.warning("Invalid result: %s", result)

        formatted_result = self.format_result(result)
        await self.bot_channel.send(f"@{context.author.display_name} {formatted_result}")

    def validate_result(self, result: str):
        return True

    def format_result(self, result: dict):
        return result
