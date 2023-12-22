import socket
import threading

from utils import Message, User, UserStatus


class Client:
    """Client class for communicating with server"""

    def __init__(self, host: str = "", port: int = 0) -> None:
        self.host = host
        self.port = port
        self.user = User

    def send(self, message: Message):
        """Send message to a specific user"""
        if self.user.status == UserStatus.AVAILABLE:
            self.user.socket.sendall(message.marshal())
        else:
            print("You are at busy status. You cannot send messages")

    def start(self, server_address: tuple[str, int]):
        """Starts the client"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        self.host = s.getsockname()[0]
        self.port = s.getsockname()[1]
        print(f'Client started at {self.host}:{self.port}')
        s.connect(server_address)

        while True:
            print()
            print("1. Login\n"
                  "2. Get list of users\n"
                  "3. Quit\n")
            option = int(input("Choose option: ").strip())

            if option == 1:
                username = input("Enter your username: ").strip()
                password = input("Enter your password: ").strip()
                self.user = User(username, s)
                self.send(Message('Login', username, 'Server', password))
                if self.receive(s) == 'Wrong password!':
                    continue
                break
            
            elif option == 2:
                s.sendall(Message('list', '', 'Server', '').marshal())

            elif option == 3:
                s.close()
                print("Quit")
                return
            
        threading.Thread(target=self.message_receiver, args=(s,)).start()
        while True:
            print()
            print("1. Send private message\n"
                  "2. Send public message\n"
                  "3. Get list of users\n"
                  "4. Quit\n")
            option = int(input("Choose option: ").strip())

            if option == 1:
                receiver = input("Enter receiver username: ").strip()
                message = input("Enter your message:\n")
                self.send(Message('Private', self.user.username, receiver, message))

            elif option == 2:
                message = input("Enter your message:\n")
                self.send(Message('Public', self.user.username, '', message))

            elif option == 3:
                self.send(Message('list', '', 'Server', ''))

            elif option == 4:
                self.send(Message('quit', self.user.username, 'Server', ''))
                self.user.socket.close()
                print("Quit")
                return
            
    def receive(self, s: socket.socket) -> str:
        """Receive and print new messages"""
        data = s.recv(4096)
        message = Message.unmarshal(data)
        print(f'\n{message.type} message from {message.sender}: {message.content}')
        return message.content

    def message_receiver(self, s: socket.socket):
        """Receive messages from server in a separate thread"""
        while True:
            try:
                self.receive(s)
            except:
                return


if __name__ == '__main__':
    client = Client()
    client.start(("127.0.0.1", 5000))
