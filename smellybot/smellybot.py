from logging import Logger
from typing import Dict, Optional, cast

from twitchio import Channel, Message
from twitchio.ext.commands import Bot, Context

from smellybot.abstract_classes import AbstractBot, AbstractChannel
from smellybot.bot_channel import BotChannel
from smellybot.channel_router_command import ChannelRouterCommand
from smellybot.config.element import ListConfigElement
from smellybot.config.secure_config import Config


class SmellyBot(Bot, AbstractBot):
    def __init__(self, config: Config, logger: Logger):

        self.logger = logger
        self.config = config
        self.channels: Dict[str, AbstractChannel] = {}

        self.channels_config = cast(ListConfigElement, config.element("channels"))

        super().__init__(token=config.element("access_token").get(),
                         prefix=config.element("prefix").get(),
                         initial_channels=self.channels_config.get())

    def get_bot_channel(self, name: str) -> Optional[AbstractChannel]:
        return self.channels.get(name)

    def join_channel(self, channel_name: str):
        self.loop.create_task(self.join_channels([channel_name]))

    def leave_channel(self, channel_name: str):
        channel_name = channel_name.lower()
        del self.channels[channel_name]
        self.config.remove_child(channel_name)

    def register_command(self, command_name: str):
        command_name = command_name.lower()
        if command_name not in self.commands:
            self.add_command(ChannelRouterCommand(self.channels, command_name, self.logger))

    async def event_join(self, twitch_channel: Channel, user):
        channel_name = twitch_channel.name.lower()
        if channel_name not in self.channels:
            channel_config = Config(channel_name, self.config, channel_restriction=channel_name.lower())
            self.channels[channel_name] = BotChannel(channel_config, self, channel_name)
            if channel_name not in self.channels_config.get():
                self.channels_config.add(channel_name)
                channel_config.element("channel.modules").add("controller")
                channel_config.element("channel.modules").add("jisho")
                channel_config.element("channel.modules").add("asksmel")
            print(f'Joined channel: {channel_name}')

        bot_channel = self.channels.get(channel_name)
        await bot_channel.set_twitch_channel(twitch_channel)

    async def event_message(self, message: Message):
        if message.echo:
            return

        channel_name = message.channel.name.lower()
        if channel_name not in self.channels:
            return

        channel = self.channels[channel_name]
        await channel.handle_message(message)

        if message.content.split(" ", 1)[0][1:] not in self.commands:
            return

        if message.echo:
            return

        await self.handle_commands(message)

    async def event_raw_usernotice(self, channel: Channel, tags: dict):
        self.logger.debug(f"Usernotice: {tags}")
        bot_channel = self.channels.get(channel.name.lower())

        if not bot_channel:
            self.logger.info("???")

        author_username = tags.get("login")

        if not author_username:
            self.logger.info("???")

        await bot_channel.handle_usernotice(author_username.lower(), tags)

    async def event_error(self, error: Exception, data: str = None):
        self.logger.error(f"{repr(error)}: {data}", exc_info=error)

    async def event_command_error(self, context: Context, error: Exception):
        self.logger.error(f"{repr(error)}: {context.author.name}: {context.message.content}", exc_info=error)
