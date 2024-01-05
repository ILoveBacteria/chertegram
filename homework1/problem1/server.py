import socket
import threading
import os
import time
from datetime import datetime

from utils import Message, User, UserStatus


class Server:
    """Server class for handling multiple clients"""

    PASSWORD_SALT = "rAND0mS4lT"

    def __init__(self, TCP_host: str = "", UDP_host: str = "", TCP_port: int = 0, UDP_port: int = 0) -> None:
        self.TCP_host = TCP_host
        self.TCP_port = TCP_port
        self.UDP_host = UDP_host
        self.UDP_port = UDP_port
        self.users: list[User] = []
        self.messages: list[Message] = []
        self.groups: dict[str, list[User]] = {}

    def send_message(self, s: socket.socket, message: Message, address: tuple[str, int] = None):
        """Send a message to client"""
        data = message.marshal()
        if s.type == socket.SocketKind.SOCK_STREAM:
            s.sendall(data)
        elif s.type == socket.SocketKind.SOCK_DGRAM:
            s.sendto(data, address)
        time.sleep(0.2)

    def send_message_to_all(self, message: Message):
        """Send a message to all clients"""
        for user in self.users:
            if user.status == UserStatus.AVAILABLE:
                self.send_message(user.socket, message)

    def receive_message(self, s: socket.socket, size: int = 4096) -> Message | tuple[Message, tuple[str, int]]:
        """Receive a message from client"""
        if s.type == socket.SocketKind.SOCK_STREAM:
            data = s.recv(size)
            return Message.unmarshal(data)
        elif s.type == socket.SocketKind.SOCK_DGRAM:
            data, server_address = s.recvfrom(size)
            return Message.unmarshal(data), server_address

    def get_users_list(self) -> str:
        """Get string list of users"""
        if len(self.users) == 0:
            return "\nThere are no users.\n"
        else:
            m = "\n"
            for user in self.users:
                m += user.username + " : " + user.status.value + "\n"
            return m

    def get_user_by_username(self, username: str) -> User:
        """Get user object by username"""
        for user in self.users:
            if user.username == username:
                return user
        return None

    def remove_user_by_username(self, username: str):
        """Remove user object from list by username"""
        for user in self.users:
            if user.username == username:
                self.users.remove(user)
                self.save_user_data_to_file()
                return
        raise ValueError(f"User {username} not found")
    
    def load_user_data_from_file(self):
        """Load user data from file"""
        if not os.path.exists('user.csv'):
            return
        with open('user.csv', 'r') as f:
            for line in f.readlines():
                username, password = line.strip().split(',')
                user = User(socket=None, username=username, status=UserStatus.OFFLINE)
                user.password = password
                self.users.append(user)

    def save_user_data_to_file(self):
        """Save user data to file"""
        with open('user.csv', 'w') as f:
            for user in self.users:
                f.write(f'{user.username},{user.password}\n')

    def set_user_status(self, username: str, userstatus: str) -> str:
        """Update status of user"""
        user = self.get_user_by_username(username)
        for status in UserStatus:
            if status == userstatus:
                user.status = status
                return
        raise ValueError(f"Status {userstatus} is invalid")

    def get_user_message_history(self, user: User) -> list[Message]:
        """Get string list of users"""
        message_history = []
        for message in self.messages:
            if message.sender == user.username or message.type == "Public":
                message_history.append(message)
            elif message.type == "AddedToGroup":
                if user.username in message.content:
                    message_history.append(message)
            elif message.type == "Group":
                if user.username in self.groups[message.receiver]:
                    message_history.append(message)
        return message_history

    def client_handler(self, s: socket.socket, address):
        """Handle a client in a separate thread"""
        print(f"Client {address[0]}:{address[1]} connected.")
        while True:
            try:
                message = self.receive_message(s)

                if message.type == "SignIn":
                    user = self.get_user_by_username(message.sender)
                    if user:
                        if user.check_password(message.content, Server.PASSWORD_SALT):
                            user.socket = s
                            user.status = UserStatus.AVAILABLE
                            print(f"{user.username} signed in.")
                            self.send_message(s, Message("Private", "Server", user.username, "Signed in successfully!"))
                            self.send_message(s, Message("Private", "Server", user.username, "This is your message history:"))
                            for m in self.get_user_message_history(user):
                                self.send_message(user.socket, m)
                            self.send_message_to_all(Message("Public", "Server", "", f"{user.username} is back online!"))
                        else:
                            self.send_message(s, Message("Private", "Server", "", "Wrong password!"))
                    else:
                        self.send_message(s, Message("Private", "Server", "", f"User {message.sender} doesn't exist."))

                elif message.type == "SignUp":
                    user = self.get_user_by_username(message.sender)
                    if user:
                        self.send_message(s, Message("Private", "Server", "", f"Username {message.sender} already exists."))
                    else:
                        user = User(s, message.sender, UserStatus.AVAILABLE)
                        user.set_password(message.content, Server.PASSWORD_SALT)
                        self.users.append(user)
                        self.save_user_data_to_file()
                        print(f"{user.username} signed up.")
                        self.send_message(s, Message("Private", "Server", user.username, "Signed up successfully!"))
                        self.send_message_to_all(Message("Public", "Server", "", f"{user.username} joined the chat!"))
                                
                elif message.type == "SetStatus":
                    self.set_user_status(message.sender, message.content)
                    print(f"{message.sender} changed status to {message.content}.")
                    self.send_message_to_all(Message("Public", "Server", "", f"{message.sender} is {message.content} now."))

                elif message.type == "DeleteAccount":
                    user = self.get_user_by_username(message.sender)
                    if user.check_password(message.content, Server.PASSWORD_SALT):
                        self.send_message(user.socket, Message("DeletedAccount", "Server", user.username, ""))
                        self.remove_user_by_username(message.sender)
                        self.save_user_data_to_file()
                        print(f"{message.sender} deleted account.")
                        self.send_message_to_all(Message("Public", "Server", "", f"{message.sender} deleted their account."))

                elif message.type == "Quit":
                    if message.sender == "":
                        print(f"Client {address[0]}:{address[1]} disconnected.")
                        s.close()
                    else:
                        user = self.get_user_by_username(message.sender)
                        user.socket.close()
                        user.socket = None
                        user.status = UserStatus.OFFLINE
                        self.send_message_to_all(Message("Public", "Server", "", f"{user.username} went offline."))
                        print(f"{user.username} went offline.")
                    return
                
                elif message.type == "Private":
                    receiver = self.get_user_by_username(message.receiver)
                    if receiver.status == UserStatus.AVAILABLE:
                        self.messages.append(message)
                        self.send_message(receiver.socket, message)
                    else:
                        self.send_message(s, Message("Private", "Server", message.sender, f"{message.receiver} is not available at the moment."))
                
                elif message.type == "Public":
                    self.messages.append(message)
                    self.send_message_to_all(message)

                elif message.type == "CreateGroup":
                    members = [self.get_user_by_username(username) for username in message.content.split(':')]
                    self.groups[message.sender] = members
                    print(f"Group {message.sender} created.")
                    message = Message("AddedToGroup", "Server", message.sender, message.content)
                    self.messages.append(message)
                    for member in members:
                        if member.status == UserStatus.AVAILABLE:
                            self.send_message(member.socket, message)

                elif message.type == "Group":
                    self.messages.append(message)
                    members = self.groups[message.receiver]
                    for member in members:
                        if member.status == UserStatus.AVAILABLE:
                            self.send_message(member.socket, message)

            except ConnectionResetError:
                break

    def tcp_handler(self, s: socket.socket):
        """Handle TCP connection in a separate thread"""
        while True:
            client_socket, client_address = s.accept()
            threading.Thread(target=self.client_handler, args=(client_socket, client_address,)).start()

    def udp_handler(self, s: socket.socket):
        """Handle UDP connection in a separate thread"""
        while True:
            message, client_address = self.receive_message(s)
            if message.type == "UserList":
                self.send_message(s, Message("UserList", "Server", "", self.get_users_list()), client_address)

    def start(self):
        """Start the TCP & UDP servers and listen for incoming connections"""
        self.load_user_data_from_file()
        TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCP_socket.bind((self.TCP_host, self.TCP_port))
        print(f"TCP Server started at {self.TCP_host}:{self.TCP_port}")
        TCP_socket.listen()
        threading.Thread(target=self.tcp_handler, args=(TCP_socket,)).start()

        UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDP_socket.bind((self.UDP_host, self.UDP_port))
        threading.Thread(target=self.udp_handler, args=(UDP_socket,)).start()
        print(f"UDP Server started at {self.UDP_host}:{self.UDP_port}")


if __name__ == '__main__':
    server = Server(TCP_port=25000, UDP_port=25001)
    server.start()