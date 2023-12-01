import socket


class UDPClient:
    """Client class for sending data to UDP servers"""

    def __init__(self, address: str = "", port: int = 0) -> None:
        self.address = address
        self.port = port

    def start(self, server_address):
        """Starts the UDP client"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((self.address, self.port))
        print(f'Client is running at {s.getsockname()}')

        while True:
            message = input("Enter your string:\n")
            s.sendto(message.encode(), server_address)

            if message != "end server":
                response, server_address = s.recvfrom(1000)
                print(response.decode(), "\n")
            else:
                s.close()
                break


class TCPClient:
    """Client class for sending data to TCP servers"""

    def __init__(self, address: str = "", port: int = 0) -> None:
        self.address = address
        self.port = port

    def start(self, server_address):
        """Starts the TCP client"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.address, self.port))
        print(f'Client is running at {s.getsockname()}')

        s.connect(server_address)

        while True:
            message = input("Enter your string:\n")
            s.send(message.encode())

            if message != "end server":
                response, connection_address = s.recvfrom(1000)
                print(response.decode(), "\n")
            else:
                s.close()
                break


def main():
    while True:
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
