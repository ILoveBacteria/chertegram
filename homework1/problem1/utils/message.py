class Message:
    def __init__(self, type: str, sender: str, receiver: str, content: str, send_time: str) -> None:
        self.type = type
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.send_time = send_time

    def marshal(self) -> bytes:
        """Marshal message into bytes
        Format: type;sender;receiver;content;send_time
        """
        return f'{self.type};{self.sender};{self.receiver};{self.content};{self.send_time}'.encode()

    @classmethod
    def unmarshal(cls, data: bytes):
        """Unmarshal bytes into message"""
        return Message(*data.decode().split(';'))
