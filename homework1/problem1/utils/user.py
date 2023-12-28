from enum import StrEnum
import socket
import hashlib


class UserStatus(StrEnum):
    AVAILABLE = 'available'
    BUSY = 'busy'
    OFFLINE = 'offline'


class User:
    def __init__(self, username: str, socket: socket.socket, status: UserStatus) -> None:
        self.username = username
        self.password = None
        self.socket = socket
        self.status = status

    def set_password(self, password: str, salt: str):
        self.password = hashlib.sha256((password + salt).encode()).hexdigest()

    def check_password(self, password: str, salt: str) -> bool:
        return self.password == hashlib.sha256((password + salt).encode()).hexdigest()