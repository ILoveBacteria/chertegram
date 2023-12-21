import socket
import threading
import datetime

from utils import Message, User, UserStatus


class Server:
    """Server class for handling multiple clients"""

    def __init__(self, host: str = "", port: int = 0) -> None:
        self.host = host
        self.port = port
        self.users = []

    def send(self, message: Message, s: socket.socket):
        """Send message to a specific user"""
        s.sendall(message.marshal())

    def send_to_all(self, message: Message):
        """Send message to all users"""
        for user in self.users:
            if user.status == UserStatus.AVAILABLE:
                self.send(message, user.socket)

    def get_users_list_str(self) -> str:
        """Get string list of users"""
        m = "\n"
        for user in self.users:
            m += user.username + "\n"
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
                return
        raise ValueError(f'User {username} not found')

    def client_handler(self, s: socket.socket):
        """Handle a client in a separate thread"""        
        while True:
            try:
                data = s.recv(255)
                message = Message.unmarshal(data)
                
                if message.type == "Server":
                    if message.content == "list":
                        self.send(Message("Server", "", "", self.get_users_list_str(), datetime.datetime.now().strftime('%H:%M')), s)
                    
                    elif message.content == "SetUsername":
                        if self.get_user_by_username(message.sender):
                            self.send(Message('Server', '', '', f'This username has already taken!', datetime.datetime.now().strftime('%H:%M')), s)
                            continue
                        user = User(message.sender, s)
                        self.users.append(user)
                        self.send_to_all(Message("Server", "", "", f'{message.sender} joined the chat. Say hello to {message.sender}!', datetime.datetime.now().strftime('%H:%M')))
                        print(f'{message.sender} joined the chat.')
                    
                    elif message.content == "quit":
                        self.get_user_by_username(message.sender).socket.close()
                        self.remove_user_by_username(message.sender)
                        self.send_to_all(Message("Server", "", "", f'{message.sender} left the chat.', datetime.datetime.now().strftime('%H:%M')))
                        print(f'{message.sender} left the chat.')
                        return
                
                elif message.type == "Private":
                    receiver = self.get_user_by_username(message.receiver)
                    if receiver.status == UserStatus.AVAILABLE:
                        self.send(message, receiver.socket)
                    else:
                        self.send(Message('Server', '', '', f'{message.receiver} is not available at the moment.', datetime.datetime.now().strftime('%H:%M')), s)
                
                elif message.type == "Public":
                    self.send_to_all(message)

            except ConnectionResetError:
                break

    def start(self):
        """Start the TCP server and listen for incoming connections"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        self.host = s.getsockname()[0]
        self.port = s.getsockname()[1]
        s.listen()
        print(f'Server started at {self.host}:{self.port}')
        
        while True:
            client_socket, client_address = s.accept()
            print(f'Client {client_address[0]}:{client_address[1]} connected')
            threading.Thread(target=self.client_handler, args=(client_socket,)).start()


if __name__ == '__main__':
    server = Server(port=5000)
    server.start()