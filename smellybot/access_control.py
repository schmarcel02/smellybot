from abc import ABC, abstractmethod

from smellybot.context import BotUser


class AccessControl(ABC):
    @classmethod
    @abstractmethod
    def name(cls):
        raise NotImplementedError()

    @abstractmethod
    def check(self, user: BotUser) -> bool:
        raise NotImplementedError()

    def __eq__(self, other):
        return type(self) is type(other)


class Everyone(AccessControl):
    @classmethod
    def name(cls):
        return "everyone"

    def check(self, user: BotUser):
        return True


class MasterOnly(AccessControl):
    @classmethod
    def name(cls):
        return "master"

    def check(self, user: BotUser):
        return "master" in user.roles


class AdminOnly(AccessControl):
    @classmethod
    def name(cls):
        return "admin"

    def check(self, user: BotUser):
        return "admin" in user.roles


class StreamerOnly(AccessControl):
    @classmethod
    def name(cls):
        return "streamer"

    def check(self, user: BotUser):
        return "streamer" in user.roles


class ModOnly(AccessControl):
    @classmethod
    def name(cls):
        return "mod"

    def check(self, user: BotUser):
        return "mod" in user.roles


class AdminPlus(AccessControl):
    @classmethod
    def name(cls):
        return "admin+"

    def check(self, user: BotUser):
        return MasterOnly().check(user) or AdminOnly().check(user)


class StreamerPlus(AccessControl):
    @classmethod
    def name(cls):
        return "streamer+"

    def check(self, user: BotUser):
        return AdminPlus().check(user) or StreamerOnly().check(user)


class ModPlus(AccessControl):
    @classmethod
    def name(cls):
        return "mod+"

    def check(self, user: BotUser):
        return AdminPlus().check(user) or ModOnly().check(user)
