import socket
import threading

from utils import Message, User, UserStatus


class Client:
    """Client class for communicating with server"""

    def __init__(self, host: str = "", TCP_port: int = 0, UDP_port: int = 0) -> None:
        self.host = host
        self.TCP_port = TCP_port
        self.UDP_port = UDP_port
        self.user = User

    def send(self, message: Message):
        """Send message to a specific user"""
        if self.user.status == UserStatus.AVAILABLE:
            self.user.socket.sendall(message.marshal())
        else:
            print("You are at busy status. You cannot send messages")

    def receive(self, s: socket.socket) -> str:
        """Receive and print new messages"""
        data = s.recv(4096)
        message = Message.unmarshal(data)
        print(f'\n{message.time_sent} {message.type} message from {message.sender}: {message.content}')
        return message.content

    def message_receiver(self, s: socket.socket):
        """Receive messages from server in a separate thread"""
        while True:
            try:
                self.receive(s)
            except:
                return
    
    def get_users_list(self, s: socket.socket, address: tuple[str, int]):
        s.sendto(Message('list', '', 'Server', '').marshal(), address)
        data, _ = s.recvfrom(255)
        message = Message.unmarshal(data)
        print(f'\n{message.time_sent} {message.type} message from {message.sender}: {message.content}')


    def start(self, server_TCP_address: tuple[str, int], server_UDP_address: tuple[str, int]):
        """Starts the client"""
        UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDP_socket.bind((self.host, self.UDP_port))
        self.host = UDP_socket.getsockname()[0]
        self.UDP_port = UDP_socket.getsockname()[1]

        TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCP_socket.bind((self.host, self.TCP_port))
        self.host = TCP_socket.getsockname()[0]
        self.TCP_port = TCP_socket.getsockname()[1]
        TCP_socket.connect(server_TCP_address)
        print(f'Client started at {self.host}:{self.TCP_port}')

        while True:
            print()
            print("1. Login / Sign Up\n"
                  "2. Get list of users\n"
                  "3. Quit\n")
            option = int(input("Choose option: ").strip())

            if option == 1:
                username = input("Enter your username: ").strip()
                password = input("Enter your password: ").strip()
                TCP_socket.sendall(Message('Login', username, 'Server', password).marshal())
                response = self.receive(TCP_socket)
                if response == 'Wrong password!':
                    continue
                elif response in ('Logged in successfully!', 'Signed up successfully!'):
                    self.user = User(username, TCP_socket)
                    break
            
            elif option == 2:
                self.get_users_list(UDP_socket, server_UDP_address)

            elif option == 3:
                TCP_socket.close()
                print("Quit")
                return
            
        threading.Thread(target=self.message_receiver, args=(TCP_socket,)).start()

        while True:
            print(f"\n{self.user.username} : {self.user.status.value}\n"
                  "1. Change status\n"
                  "2. Send private message\n"
                  "3. Send public message\n"
                  "4. Get list of users\n"
                  "5. Quit\n")
            option = int(input("Choose option: ").strip())

            if option == 1:
                if self.user.status == UserStatus.AVAILABLE:
                    self.send(Message('SetStatus', self.user.username, 'Server', UserStatus.BUSY.value))
                    self.user.status = UserStatus.BUSY
                elif self.user.status == UserStatus.BUSY:
                    self.user.status = UserStatus.AVAILABLE
                    self.send(Message('SetStatus', self.user.username, 'Server', UserStatus.AVAILABLE.value))

            elif option == 2:
                receiver = input("Enter receiver username: ").strip()
                message = input("Enter your message:\n")
                self.send(Message('Private', self.user.username, receiver, message))

            elif option == 3:
                message = input("Enter your message:\n")
                self.send(Message('Public', self.user.username, '', message))

            elif option == 4:
                self.get_users_list(UDP_socket, server_UDP_address)

            elif option == 5:
                self.send(Message('quit', self.user.username, 'Server', ''))
                self.user.socket.close()
                print("Quit")
                return


if __name__ == '__main__':
    client = Client()
    client.start(("127.0.0.1", 25000), ("127.0.0.1", 25001))
