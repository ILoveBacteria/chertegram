import socket


class Client:
    """Client class for sending data to servers"""

    def __init__(self, host: str = "", port: int = 0) -> None:
        self.host = host
        self.port = port

    def start(self, server_address):
        """Starts the client"""
        pass


class UDPClient(Client):
    """Client class for sending data to UDP servers"""

    def start(self, server_address: tuple[str, int]):
        """Starts the UDP client"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((self.host, self.port))
        self.host = s.getsockname()[0]
        self.port = s.getsockname()[1]
        print(f'Client is running at {s.getsockname()[0]}:{s.getsockname()[1]}')

        while True:
            message = input("\nEnter your string:\n")
            s.sendto(message.encode(), server_address)

            if message != "end server":
                response, server_address = s.recvfrom(4096)
                print(response.decode())
            else:
                s.close()
                break


class TCPClient(Client):
    """Client class for sending data to TCP servers"""

    def start(self, server_address: tuple[str, int]):
        """Starts the TCP client"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        self.host = s.getsockname()[0]
        self.port = s.getsockname()[1]
        print(f'Client is running at {s.getsockname()[0]}:{s.getsockname()[1]}')

        s.connect(server_address)

        while True:
            message = input("\nEnter your string:\n")
            s.sendall(message.encode())

            if message != "end server":
                response, connection_address = s.recvfrom(4096)
                print(response.decode())
            else:
                s.close()
                break


def main():
    while True:
        print()
        print("1. UDP")
        print("2. TCP")
        print("3. Quit")
        option = int(input("Choose option: ").strip())

        if option == 1:
            client = UDPClient()
            client.start(("127.0.0.1", 23450))
        if option == 2:
            client = TCPClient()
            client.start(("127.0.0.1", 23451))
        if option == 3:
            print("Quit")
            break


if __name__ == "__main__":
    main()
