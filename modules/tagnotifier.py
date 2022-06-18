from config import ModuleConfig
from smellybot import BotModule, BotChannel


class TagNotifier(BotModule):
    def __init__(self, bot_channel: BotChannel, module_config: ModuleConfig):
        super().__init__(bot_channel, module_config)

    @classmethod
    def name(cls):
        return "tagnotifier"

    async def notify_if_present(self, original_channel: str, original_author_username: str, target_username: str,
                                original_message: str, is_reply: bool = False) -> bool:
        if not self.module_config.is_enabled():
            self.logger.debug("Tagnotifier is disabled in this channel")
            return False

        if original_author_username == self.module_config.bot_config.is_bot_user(original_author_username):
            self.logger.error("A message from SMELsBot should never reach this method")
            exit(1)

        for user in self.bot_channel.channel.chatters:
            if user.name.lower() == target_username.lower():
                await self.notify(original_channel, original_author_username,
                                  target_username, original_message, is_reply)
                return True
        return False

    async def notify(self, original_channel: str, original_author_username: str, target_username: str,
                     original_message: str, is_reply: bool = False):
        if not self.module_config.is_enabled():
            self.logger.debug("Tagnotifier is disabled in this channel")
            return

        if original_author_username == self.module_config.bot_config.is_bot_user(original_author_username):
            self.logger.error("A message from SMELsBot should never reach this method")
            exit(1)

        notification_reason = "replied to you" if is_reply else "tagged you"

        notification = f"@{target_username}: @{original_author_username} {notification_reason} in @{original_channel}'s chat: {original_message}"
        self.bot_channel.send(notification)
