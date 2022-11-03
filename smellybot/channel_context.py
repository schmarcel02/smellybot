from typing import Optional

from smellybot.context import MessageContext


class ChannelContext:
    def __init__(self):
        self.previous_context: Optional[MessageContext] = None
        self.current_context: Optional[MessageContext] = None
