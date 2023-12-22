from enum import IntEnum
import socket


class UserStatus(IntEnum):
    AVAILABLE = 1
    BUSY = 2


class User:
    def __init__(self, username: str, socket: socket.socket) -> None:
        self.username = username
        self.socket = socket
        self.status = UserStatus.AVAILABLE
