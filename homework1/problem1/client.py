import socket
import threading
import time
from datetime import datetime

from utils import Message, User, UserStatus


class Client:
    """Client class for communicating with server"""

    def __init__(self, TCP_host: str = "", UDP_host: str = "", TCP_port: int = 0, UDP_port: int = 0) -> None:
        self.TCP_host = TCP_host
        self.TCP_port = TCP_port
        self.UDP_host = UDP_host
        self.UDP_port = UDP_port
        self.user: User = None
        self.groups: dict[int, str] = {}

    def message_sender(self, s: socket.socket, message: Message, address: tuple[str, int] = None) -> bool:
        """Send a message to server"""
        if self.user is not None:
            if self.user.status == UserStatus.BUSY:
                if message.type != "Quit":
                    print("Your status is busy. You cannot send messages.")
                    return False
        data = message.marshal()
        if s.type == socket.SocketKind.SOCK_STREAM:
            s.sendall(data)
        elif s.type == socket.SocketKind.SOCK_DGRAM:
            s.sendto(data, address)
        return True

    def message_receiver(self, s: socket.socket, size: int = 4096) -> str:
        """Receive a message from server"""
        if s.type == socket.SocketKind.SOCK_STREAM:
            data = s.recv(size)
        elif s.type == socket.SocketKind.SOCK_DGRAM:
            data, server_address = s.recvfrom(size)
        message = Message.unmarshal(data)
        time = datetime.strptime(message.time, "%Y-%m-%d %H:%M:%S.%f").strftime("%H:%M:%S")
        
        if message.sender != "Server" or message.type == "Private":
            if message.type == "Group":
                print(f"\n{time} {message.type} message from {message.sender} in group {message.receiver}: {message.content}\n")
            else:
                print(f"\n{time} {message.type} message from {message.sender}: {message.content}\n")
        elif message.sender == "Server":
            if message.type == "UserList":
                print(f"\n{time} List of users: {message.content}\n")
            elif message.type == "DeletedAccount":
                self.user = None
            elif message.type == "AddedToGroup":
                self.groups[len(self.groups)+10] = message.receiver
                print(f"\n{time} You were added to group: {message.receiver}\n")

        return message.content

    def receiver_handler(self, s: socket.socket):
        """Handle receiving messages from TCP server"""
        while True:
            try:
                self.message_receiver(s)
            except:
                return


    def sign_in(self, s: socket.socket) -> bool:
        username = input("Enter your username: ").strip()
        password = input("Enter your password: ").strip()
        self.message_sender(s, Message("SignIn", username, "Server", password))
        response = self.message_receiver(s)
        if response == "Wrong password!":
            return False
        elif response == "Signed in successfully!":
            self.user = User(s, username, UserStatus.AVAILABLE)
            return True

    def sign_up(self, s: socket.socket) -> bool:
        username = input("Enter your username: ").strip()
        password = input("Enter your password: ").strip()
        self.message_sender(s, Message("SignUp", username, "Server", password))
        response = self.message_receiver(s)
        if response == "Wrong password!":
            return False
        elif response == "Signed up successfully!":
            self.user = User(s, username, UserStatus.AVAILABLE)
            return True

    def get_users_list(self, s: socket.socket, address: tuple[str, int]):
        if self.message_sender(s, Message("UserList", "", "Server", ""), address):
            self.message_receiver(s)

    def quit(self, s: socket.socket) -> bool:
        if self.user is None:
            self.message_sender(s, Message("Quit", "", "Server", ""))
        else:
            self.message_sender(s, Message("Quit", self.user.username, "Server", ""))
        s.close()
        print("Quited")
        return True


    def change_status(self):
        if self.user.status == UserStatus.AVAILABLE:
            self.message_sender(self.user.socket, Message("SetStatus", self.user.username, "Server", UserStatus.BUSY.value))
            self.user.status = UserStatus.BUSY
        elif self.user.status == UserStatus.BUSY:
            self.user.status = UserStatus.AVAILABLE
            self.message_sender(self.user.socket, Message("SetStatus", self.user.username, "Server", UserStatus.AVAILABLE.value))

    def delete_account(self) -> bool:
        password = input("Enter your password: ").strip()
        self.message_sender(self.user.socket, Message("DeleteAccount", self.user.username, "Server", password))
        time.sleep(0.2)
        if self.user is None:
            return True
        return False

    def send_private_message(self):
        receiver = input("Enter receiver username: ").strip()
        message = input("Enter your message:\n")
        self.message_sender(self.user.socket, Message("Private", self.user.username, receiver, message))

    def send_public_message(self):
        message = input("Enter your message:\n")
        self.message_sender(self.user.socket, Message("Public", self.user.username, "", message))

    def create_group(self):
        groupname = input("Enter group name: ").strip()
        print("Enter member usernames and press enter. Press an extra enter to stop.")
        members = ""
        while True:
            member = input("Member: ").strip()
            if member == "":
                break
            else:
                members += member + ':'
        members += self.user.username
        print(members)
        self.message_sender(self.user.socket, Message("CreateGroup", groupname, "Server", members))        

    def send_group_message(self, groupid: int):
        message = input("Enter your message:\n")
        self.message_sender(self.user.socket, Message("Group", self.user.username, self.groups[groupid], message))

    def menu(self) -> int:
        if self.user is None:
            options = ["Sign In",
                       "Sign Up",
                       "Get list of users",
                       "Quit"]
            for i, option in enumerate(options):
                print(str(i+1) + ". " + option)
            print()
            return int(input("Choose option: ").strip())
        else:
            print(f"\n{self.user.username} : {self.user.status.value}")
            options = ["Change status",
                       "Send public message",
                       "Send private message",
                       "Create group",
                       "Delete account",
                       "Get list of users",
                       "Quit"]
            for i, option in enumerate(options):
                print(str(i+1) + ". " + option)
            print()
            for i in self.groups:
                print(str(i) + ". Send message to group " + self.groups[i])
            print()
            return int(input("Choose option: ").strip())

    def start(self, server_TCP_address: tuple[str, int], server_UDP_address: tuple[str, int]):
        """Starts the client"""
        TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCP_socket.bind((self.TCP_host, self.TCP_port))
        self.TCP_host = TCP_socket.getsockname()[0]
        self.TCP_port = TCP_socket.getsockname()[1]
        TCP_socket.connect(server_TCP_address)
        print(f'Client started at {self.TCP_host}:{self.TCP_port}')

        UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDP_socket.bind((self.UDP_host, self.UDP_port))
        self.UDP_host = UDP_socket.getsockname()[0]
        self.TCP_port = UDP_socket.getsockname()[1]

        while True:
            option = self.menu()

            if option == 1:
                if self.sign_in(TCP_socket):
                    break

            elif option == 2:
                if self.sign_up(TCP_socket):
                    break

            elif option == 3:
                self.get_users_list(UDP_socket, server_UDP_address)

            elif option == 4:
                if self.quit(TCP_socket):
                    return
            
        threading.Thread(target=self.receiver_handler, args=(TCP_socket,)).start()

        while True:
            option = self.menu()

            if option == 1:
                self.change_status()

            elif option == 2:
                self.send_public_message()

            elif option == 3:
                self.send_private_message()

            elif option == 4:
                self.create_group()

            elif option == 5:
                if self.delete_account():
                    if self.quit(TCP_socket):
                        return

            elif option == 6:
                self.get_users_list(UDP_socket, server_UDP_address)

            elif option == 7:
                if self.quit(self.user.socket):
                    return
            
            elif option > 9:
                self.send_group_message(option)


if __name__ == '__main__':
    client = Client()
    client.start(("127.0.0.1", 25000), ("127.0.0.1", 25001))
