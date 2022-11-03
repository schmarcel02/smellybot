class ChatException(Exception):
    def __init__(self, chat_message: str = None, log_message: str = None):
        self.chat_message = chat_message
        self.log_message = log_message or chat_message
        self.args = chat_message, log_message
