import re
from typing import Dict, Tuple

from datetime import datetime, timedelta
from twitchio import Message

from config import ModuleConfig
from smellybot import BotModule, BotChannel


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

    def __init__(self, bot_channel: BotChannel, module_config: ModuleConfig):
        super().__init__(bot_channel, module_config)

    @classmethod
    def name(cls):
        return "tagsniffer"

    async def handle_message(self, message: Message):
        if self.module_config.bot_config.is_bot_user(message.author.name):
            return

        matches = self.TAG_REGEX.findall(message.content)
        if not matches:
            return

        for match in matches:
            username = match
            if self.user_is_in_channel(username):
                return
            self.logger.info(f"{message.author.name}: {message.content}")

            channel_name = reply_cache.get(message.author.name, self.bot_channel.channel_name, username)
            if channel_name:
                if await self.notify_in_channel_if_present(self.bot_channel.channel_name, message.author.name,
                                                           channel_name, username, message.content, is_reply=True):
                    return

            for channel_name in self.bot_channel.smelly_bot.channels:
                if await self.notify_in_channel_if_present(self.bot_channel.channel_name, message.author.name,
                                                           channel_name, username, message.content, is_reply=False):
                    return
            self.logger.info(f"User '{username}' is nowhere to be found")

    async def notify_in_channel_if_present(self, source_channel: str, source_username: str, target_channel: str,
                                           target_user: str, original_message: str, is_reply: bool = False):
        bot_channel = self.bot_channel.smelly_bot.channels.get(target_channel.lower())
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
        for user in self.bot_channel.channel.chatters:
            if user.name.lower() == username.lower():
                return True
        return False
