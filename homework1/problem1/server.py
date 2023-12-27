import socket
import threading
import os

from utils import Message, User, UserStatus


class Server:
    """Server class for handling multiple clients"""
    PASSWORD_SALT = 'rAND0mS4lT'

    def __init__(self, host: str = "", TCP_port: int = 0, UDP_port: int = 0) -> None:
        self.host = host
        self.TCP_port = TCP_port
        self.UDP_port = UDP_port
        self.users = []
        self.messages = []

    def send(self, message: Message, s: socket.socket) -> bool:
        """Send message to a specific user"""
        s.sendall(message.marshal())
        return True

    def send_to_all(self, message: Message):
        """Send message to all users"""
        for user in self.users:
            if user.status == UserStatus.AVAILABLE and user.socket is not None:
                self.send(message, user.socket)

    def get_users_list_str(self) -> str:
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
        raise ValueError(f'User {username} not found')
    
    def load_user_data_from_file(self):
        """Load user data from file"""
        if not os.path.exists('user.csv'):
            return
        with open('user.csv', 'r') as f:
            for line in f.readlines():
                username, password = line.strip().split(',')
                user = User(username=username, socket=None)
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
        raise ValueError(f'Status {userstatus} not found')
        

    def client_handler(self, s: socket.socket):
        """Handle a client in a separate thread"""
        while True:
            try:
                data = s.recv(255)
                message = Message.unmarshal(data)
                
                if message.type == "Login":
                    user = self.get_user_by_username(message.sender)
                    if user:
                        if user.check_password(message.content, Server.PASSWORD_SALT):
                            user.socket = s
                            self.send(Message('Private', 'Server', message.sender, 'Logged in successfully!'), s)
                            print(f'{message.sender} joined the chat.')
                            message_history = [m.content for m in self.messages if m.sender == message.sender]
                            if message_history:
                                message_history.insert(0, f'This is your message history:')
                                self.send(Message('Private', 'Server', message.sender, '\n'.join(message_history)), s)
                            self.send_to_all(Message('Public', 'Server', '', f'{message.sender} joined the chat. Say hello to {message.sender}!'))
                        else:
                            self.send(Message('Private', 'Server', message.sender, 'Wrong password!'), s)
                    else:
                        user = User(message.sender, s)
                        self.send(Message('Private', 'Server', message.sender, 'Signed up successfully!'), s)
                        user.set_password(message.content, Server.PASSWORD_SALT)
                        self.users.append(user)
                        self.save_user_data_to_file()
                        print(f'{message.sender} joined the chat.')
                        self.send_to_all(Message('Public', 'Server', '', f'{message.sender} joined the chat. Say hello to {message.sender}!'))
                
                elif message.type == "SetStatus":
                    self.set_user_status(message.sender, message.content)
                    print(f'{message.sender} changed status to {message.content}.')
                    self.send_to_all(Message('Public', 'Server', '', f'{message.sender} is {message.content} now.'))

                elif message.type == "quit":
                    user = self.get_user_by_username(message.sender)
                    user.socket.close()
                    user.socket = None
                    self.send_to_all(Message('Public', 'Server', '', f'{message.sender} left the chat.'))
                    print(f'{message.sender} left the chat.')
                    return
                
                elif message.type == "Private":
                    receiver = self.get_user_by_username(message.receiver)
                    if receiver.status == UserStatus.AVAILABLE:
                        if self.send(message, receiver.socket):
                            self.messages.append(message)
                    else:
                        self.send(Message('Private', 'Server', message.sender, f'{message.receiver} is not available at the moment.'), s)
                
                elif message.type == "Public":
                    self.send_to_all(message)
                    self.messages.append(message)

            except ConnectionResetError:
                break

    def udp_handler(self, s: socket.socket):
        """Handle UDP connection in a separate thread"""
        while True:
            message, client_address = s.recvfrom(255)
            if Message.unmarshal(message).type == 'list':
                s.sendto(Message('Private', 'Server', '', self.get_users_list_str()).marshal(), client_address)

    def start(self):
        """Start the UDP & TCP servers and listen for incoming connections"""
        self.load_user_data_from_file()
        UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDP_socket.bind((self.host, self.UDP_port))
        threading.Thread(target=self.udp_handler, args=(UDP_socket,)).start()
        print(f'UDP Server started at {self.host}:{self.UDP_port}')

        TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCP_socket.bind((self.host, self.TCP_port))
        print(f'TCP Server started at {self.host}:{self.TCP_port}')
        TCP_socket.listen()
        while True:
            client_socket, client_address = TCP_socket.accept()
            print(f'Client {client_address[0]}:{client_address[1]} connected')
            threading.Thread(target=self.client_handler, args=(client_socket,)).start()


if __name__ == '__main__':
    server = Server(TCP_port=25000, UDP_port=25001)
    server.start()