import re


from smellybot.bot_module import BotModule
from smellybot.config.secure_config import Config
from smellybot.context import MessageContext


class Amogus(BotModule):
    AMONG_US_REGEX = re.compile(r"\b(among us|amogus)\b", re.IGNORECASE)
    SUS_REGEX = re.compile(r"\b(sus|sussy)\b", re.IGNORECASE)

    def __init__(self, config: Config, bot_channel):
        super().__init__(config, bot_channel)

    @classmethod
    def name(cls):
        return "amogus"

    async def _handle_message(self, context: MessageContext):
        if context.author.username.lower() == "smelsbot":
            return

        if self.AMONG_US_REGEX.search(context.message):
            self.logger.info(f"{context.author.username}: {context.message}")
            await self.send_sus(context.author.display_name)
            return

        #if self.SUS_REGEX.search(context.message):
        #    self.logger.info(f"{context.author.username}: {context.message}")
        #    await self.send_amogus(context.author.display_name)
        #    return

    async def send_sus(self, username: str):
        await self.bot_channel.send(f"@{username} sus.")

    async def send_amogus(self, username: str):
        await self.bot_channel.send(f"@{username} amogus ඞ")
