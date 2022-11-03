from typing import Set


class BotUser:
    def __init__(self, display_name: str):
        self.username = display_name.lower()
        self.display_name = display_name
        self.roles: Set[str] = set()

    def has_role(self, role: str):
        return role in self.roles

    def add_role(self, role: str):
        self.roles.add(role)

    def remove_role(self, role: str):
        self.roles.remove(role)

    def __eq__(self, other):
        return isinstance(other, BotUser) and self.username == other.username


class MessageContext:
    def __init__(self, bot, channel, author: BotUser, message: str):
        self.bot = bot
        self.channel = channel
        self.author = author
        self.message = message
