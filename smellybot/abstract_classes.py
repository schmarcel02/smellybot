from abc import ABC, abstractmethod
from typing import List, Dict, Any

from twitchio import Message
from twitchio.ext.commands import Context

from smellybot.context import MessageContext


class AbstractBot(ABC):
    @abstractmethod
    async def join_channel(self, channel_name: str):
        raise NotImplementedError()

    @abstractmethod
    async def leave_channel(self, channel_name: str):
        raise NotImplementedError()

    @abstractmethod
    def register_command(self, command_name: str):
        raise NotImplementedError()


class AbstractChannel(ABC):
    @abstractmethod
    async def add_module(self, module_name: str):
        raise NotImplementedError()

    @abstractmethod
    async def remove_module(self, module_name: str):
        raise NotImplementedError()

    @abstractmethod
    async def send(self, message: str):
        raise NotImplementedError()

    @abstractmethod
    async def run_command(self, command_name: str, ctx: Context):
        raise NotImplementedError()

    @abstractmethod
    async def handle_message(self, message: Message):
        raise NotImplementedError()

    @abstractmethod
    async def handle_usernotice(self, author_username: str, tags: dict):
        raise NotImplementedError()


class AbstractModule(ABC):
    @staticmethod
    @abstractmethod
    def name() -> str:
        raise NotImplementedError()

    @abstractmethod
    async def on_ready(self):
        raise NotImplementedError()

    @abstractmethod
    async def run_command(self, command_name: str, context: MessageContext):
        raise NotImplementedError()

    @abstractmethod
    async def handle_message(self, context: MessageContext):
        raise NotImplementedError()

    @abstractmethod
    async def handle_usernotice(self, author_username: str, tags: dict):
        raise NotImplementedError()


class AbstractCommand(ABC):
    @abstractmethod
    def get_name_and_aliases(self) -> List[str]:
        raise NotImplementedError()

    @abstractmethod
    async def invoke(self, context: MessageContext, arguments: str, command: str, head: str, **kwargs):
        raise NotImplementedError()
