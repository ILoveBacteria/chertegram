class Message:
    def __init__(self, type: str, sender: str, receiver: str, content: str) -> None:
        self.type = type
        self.sender = sender
        self.receiver = receiver
        self.content = content

    def marshal(self) -> bytes:
        """Marshal message into bytes
        Format: sender;receiver;content
        """
        return f'{self.type};{self.sender};{self.receiver};{self.content}'.encode()

    @classmethod
    def unmarshal(cls, data: bytes):
        """Unmarshal bytes into message"""
        return Message(*data.decode().split(';'))
