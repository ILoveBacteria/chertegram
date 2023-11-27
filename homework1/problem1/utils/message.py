class Message:
    def __init__(self, sender: str, receiver: str, content: str) -> None:
        self.sender = sender
        self.receiver = receiver
        self.content = content

    def marshal(self) -> bytes:
        return f'{self.sender};{self.receiver};{self.content}'.encode()

    @classmethod
    def unmarshal(data: bytes) -> Message:
        return Message(*data.decode().split(';'))
