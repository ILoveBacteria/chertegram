import socket


class User:
    def __init__(self, username: str, socket: socket.socket) -> None:
        self.username = username
        self.socket = socket
