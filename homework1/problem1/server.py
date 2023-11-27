import socket
import threading

from utils import Message
from utils import User


class Server:
    def __init__(self, port: int) -> None:
        self.port = port
        self.users = []

    def send_to_all(self, message: Message):
        for user in self.users:
            self.send(message, user.socket)

    def send(self, message: Message, s: socket.socket):
        s.send(message.marshal())

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', self.port))
        s.listen()
        print(f'Server started at port {self.port}')
        while True:
            client_socket, client_address = s.accept()
            print(f'Client {client_address} connected')
            threading.Thread(target=self.client_handler, args=(client_socket,)).start()

    def get_user_by_username(self, username: str) -> User:
        for user in self.users:
            if user.username == username:
                return user
        raise ValueError(f'User {username} not found')

    def client_handler(self, s: socket.socket):
        s.send('Enter your username: '.encode())
        username = s.recv(255).decode()
        user = User(username, s)
        self.users.append(user)
        self.send_to_all(Message(f'{username} joined the chat. Say hello to {username}!'))
        while True:
            try:
                data = s.recv(255)
                message = Message.unmarshal(data)
                if message.receiver:
                    self.send(message, self.get_user_by_username(message.receiver).socket)
                else:
                    self.send_to_all(message)
            except ConnectionResetError:
                break
