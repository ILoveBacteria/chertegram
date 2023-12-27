from datetime import datetime


class Message:
    def __init__(self, type: str, sender: str, receiver: str, content: str, time_sent: str = None) -> None:
        self.type = type
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.time_sent = time_sent or datetime.now().strftime('%H:%M:%S')

    def marshal(self) -> bytes:
        """Marshal message into bytes
        Format: type;sender;receiver;content;time_sent
        """
        return f'{self.type};{self.sender};{self.receiver};{self.content};{self.time_sent}'.encode()

    @classmethod
    def unmarshal(cls, data: bytes):
        """Unmarshal bytes into message"""
        print(data.decode().split(';'))
        return Message(*data.decode().split(';'))
