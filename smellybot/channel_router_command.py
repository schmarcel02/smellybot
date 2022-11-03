from logging import Logger
from typing import Dict

from twitchio.ext.commands import Command, Context

from smellybot.abstract_classes import AbstractChannel


class ChannelRouterCommand(Command):
    def __init__(self, channels: Dict[str, AbstractChannel], command_name: str, logger: Logger):
        super().__init__(command_name, self.route)
        self.channels = channels
        self.logger = logger

    async def route(self, ctx: Context):
        channel_name = ctx.channel.name.lower()
        channel = self.channels.get(channel_name)
        if not channel:
            self.logger.error("Channel '%s' not found", channel_name, exc_info=True)
        await channel.run_command(self.name, ctx)
