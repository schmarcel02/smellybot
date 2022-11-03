import re
from typing import Dict, Tuple

from datetime import datetime, timedelta

from smellybot.bot_module import BotModule
from smellybot.config.secure_config import Config
from smellybot.context import MessageContext


class ReplyCache:
    def __init__(self):
        self.cache: Dict[Tuple[str, str, str], Tuple[datetime, str]] = {}

    def add(self, source_username: str, source_channel: str, target_username: str, target_channel: str):
        now = datetime.now()
        self.cache[(source_username.lower(), source_channel.lower(), target_username.lower())] = (now, target_channel.lower())

    def get(self, source_username: str, source_channel: str, target_username: str):
        entry = self.cache.get((source_username.lower(), source_channel.lower(), target_username.lower()))
        if not entry or datetime.now() - entry[0] > timedelta(minutes=15):
            return None
        return entry[1]


reply_cache = ReplyCache()


class TagSniffer(BotModule):
    TAG_REGEX = re.compile(r"@([a-zA-Z0-9_]+)\b")

    def __init__(self, config: Config, bot_channel):
        super().__init__(config, bot_channel)

        self.bot_user_config = config.element("bot_username")

    @classmethod
    def name(cls):
        return "tagsniffer"

    async def _handle_message(self, context: MessageContext):
        if context.author.username == self.bot_user_config.get():
            return

        if len(self.bot_channel.twitch_channel.chatters) < 8:
            return

        matches = self.TAG_REGEX.findall(context.message)
        if not matches:
            return

        for match in matches:
            username = match
            if username.lower() == self.bot_channel.name.lower():
                return
            if self.user_is_in_channel(username):
                return
            self.logger.info(f"{context.author.username}: {context.message}")

            channel_name = reply_cache.get(context.author.username, self.bot_channel.name, username)
            if channel_name:
                if await self.notify_in_channel_if_present(self.bot_channel.name, context.author.username,
                                                           channel_name, username, context.message, is_reply=True):
                    return

            for channel_name in self.bot_channel.bot.channels:
                if channel_name.lower() == self.bot_channel.name.lower():
                    continue
                if await self.notify_in_channel_if_present(self.bot_channel.name, context.author.username,
                                                           channel_name, username, context.message, is_reply=False):
                    return
            self.logger.info(f"User '{username}' is nowhere to be found")

    async def notify_in_channel_if_present(self, source_channel: str, source_username: str, target_channel: str,
                                           target_user: str, original_message: str, is_reply: bool = False):
        bot_channel = self.bot_channel.bot.channels.get(target_channel.lower())
        if not bot_channel:
            self.logger.warning(f"Channel '{target_channel}' not found")
            return False
        tagnotifier = bot_channel.modules.get("tagnotifier")
        if not tagnotifier:
            self.logger.warning(f"Channel '{target_channel}' has no tagnotifier module")
            return False
        if await tagnotifier.notify_if_present(source_channel, source_username, target_user, original_message, is_reply):
            reply_cache.add(target_user, target_channel, source_username, source_channel)
            return True

    def user_is_in_channel(self, username: str):
        for user in self.bot_channel.twitch_channel.chatters:
            if user.name.lower() == username.lower():
                return True
        return False
