import time

from math import ceil

from smellybot.bot_module import BotModule
from smellybot.config.secure_config import Config


class Crumber(BotModule):

    def __init__(self, config: Config, bot_channel):
        super().__init__(config, bot_channel)

    @classmethod
    def name(cls):
        return "crumber"

    async def _handle_usernotice(self, author_username: str, tags: dict):
        if "login" not in tags or tags["login"] != "bread_crumbs0":
            return
        if "msg-param-mass-gift-count" not in tags:
            return

        try:
            number_of_subs = int(tags["msg-param-mass-gift-count"])
        except ValueError:
            self.logger.warning("Invalid value for number of gift subs: %s", tags["msg-param-mass-gift-count"])
            return
        self.logger.info(f"{author_username} gifted {number_of_subs} subs")

        if number_of_subs > 0:
            await self.send_gigabread(author_username, number_of_subs)

    async def send_gigabread(self, username: str, number_of_subs: int):
        gigabread = "GIGABREAD " * ceil(number_of_subs / 5)
        time.sleep(2)
        await self.bot_channel.send(gigabread)
