from datetime import datetime


class Message:
    def __init__(self, type: str, sender: str, receiver: str, content: str, time: datetime = None) -> None:
        self.type = type
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.time = time or datetime.now()

    def marshal(self) -> bytes:
        """Marshal message into bytes
        Format: type;sender;receiver;content;time_sent
        """
        return f'{self.type};{self.sender};{self.receiver};{self.content};{self.time}'.encode()

    @classmethod
    def unmarshal(cls, data: bytes):
        """Unmarshal bytes into message"""
        return Message(*data.decode().split(';'))
