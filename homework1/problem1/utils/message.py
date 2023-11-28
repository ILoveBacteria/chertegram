class Message:
    def __init__(self, sender: str, receiver: str, content: str) -> None:
        self.sender = sender
        self.receiver = receiver
        self.content = content

    def marshal(self) -> bytes:
        """Marshal message into bytes
        Format: sender;receiver;content
        """
        return f'{self.sender};{self.receiver};{self.content}'.encode()

    @classmethod
    def unmarshal(cls, data: bytes):
        """Unmarshal bytes into message"""
        return Message(*data.decode().split(';'))
