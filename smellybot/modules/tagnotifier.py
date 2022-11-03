from smellybot.bot_module import BotModule
from smellybot.config.secure_config import Config


class TagNotifier(BotModule):

    def __init__(self, config: Config, bot_channel):
        super().__init__(config, bot_channel)

        self.bot_user_config = config.element("bot_username")

    @classmethod
    def name(cls):
        return "tagnotifier"

    async def notify_if_present(self, original_channel: str, original_author_username: str, target_username: str,
                                original_message: str, is_reply: bool = False) -> bool:
        if not self.enabled_config.get():
            self.logger.debug("Tagnotifier is disabled in this channel")
            return False

        if original_author_username == self.bot_user_config.get():
            self.logger.error("A message from SMELsBot should never reach this method")
            exit(1)

        if len(self.bot_channel.twitch_channel.chatters) < 8:
            return False

        for user in self.bot_channel.twitch_channel.chatters:
            if user.name.lower() == target_username.lower():
                await self.notify(original_channel, original_author_username,
                                  target_username, original_message, is_reply)
                return True
        return False

    async def notify(self, original_channel: str, original_author_username: str, target_username: str,
                     original_message: str, is_reply: bool = False):
        if not self.enabled_config.get():
            self.logger.debug("Tagnotifier is disabled in this channel")
            return

        if original_author_username.lower() == self.bot_user_config.get():
            self.logger.error("A message from SMELsBot should never reach this method")
            exit(1)

        notification_reason = "replied to you" if is_reply else "tagged you"

        notification = f"@{target_username}: @{original_author_username} {notification_reason} in @{original_channel}'s chat: {original_message}"
        self.bot_channel.send(notification)
