from abc import abstractmethod, ABC


class ChatSerializable(ABC):
    @classmethod
    @abstractmethod
    def from_chat_string(cls, string: str):
        raise NotImplementedError()

    @abstractmethod
    def to_chat_string(self, string: str):
        raise NotImplementedError()
