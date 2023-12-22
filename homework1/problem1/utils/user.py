from enum import IntEnum
import socket
import hashlib


class UserStatus(IntEnum):
    AVAILABLE = 1
    BUSY = 2


class User:
    def __init__(self, username: str, socket: socket.socket) -> None:
        self.username = username
        self.password = None
        self.socket = socket
        self.status = UserStatus.AVAILABLE

    def set_password(self, password: str, salt: str):
        self.password = hashlib.sha256((password + salt).encode()).hexdigest()

    def check_password(self, password: str, salt: str) -> bool:
        return self.password == hashlib.sha256((password + salt).encode()).hexdigest()