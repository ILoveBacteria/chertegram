import socket
import threading
from collections import Counter


class Server:
    """Server class for handling UDP & TCP clients"""

    def __init__(self, protocol: str, host: str = "", port: int = 0) -> None:
        self.protocol = protocol
        self.host = host
        self.port = port

    def udp_response(self, message: str) -> str:
        """Generates requested response for UDP clients"""
        result = message[::-1].upper()
        count = Counter(result)
        return f'{result} , {max(count, key=count.get).upper()}'

    def tcp_response(self, message: str) -> str:
        """Generates requested response for TCP clients"""
        result = message.lower()
        count = Counter(result)

        subs = {'a': 0, 'b': 0, 'c': 1, 'd': 1, 'e': 2, 'f': 2,
                'g': 3, 'h': 3, 'i': 4, 'j': 4, 'k': 5, 'l': 5,
                'm': 6, 'n': 6, 'o': 7, 'p': 7, 'q': 8, 'r': 8,
                's': 9, 't': 9, 'u': 10, 'v': 10, 'w': 11, 'x': 11,
                'y': 12, 'z': 12}

        for c in result:
            if c in subs:
                result = result.replace(c, str(subs[c]))

        min_frequency = count[min(count, key=count.get)]
        max_frequency_value = 0

        for c in count:
            if c in subs:
                if count[c] == min_frequency:
                    if subs[c] > max_frequency_value:
                        max_frequency_value = subs[c]

        return f'{result} , {str(max_frequency_value)}'

    def udp_handler(self, s: socket.socket):
        """Handles all UDP clients"""
        while True:
            message, client_address = s.recvfrom(4096)
            print()
            print(f'UDP message from {client_address[0]}:{client_address[1]}')
            message = message.decode()
            print(message)

            if message != "end server":
                message = self.udp_response(message)
                s.sendto(message.encode(), client_address)
                print(message)
            else:
                print(f'{client_address[0]}:{client_address[1]} ended transmitting.')

    def tcp_handler(self, s: socket.socket):
        """Handles a TCP client in a separate thread"""
        while True:
            message, client_address = s.recvfrom(4096)
            print()
            print(f'TCP message from {s.getpeername()[0]}:{s.getpeername()[1]}')
            message = message.decode()
            print(message)

            if message != "end server":
                message = self.tcp_response(message)
                s.sendall(message.encode())
                print(message)
            else:
                print(f'{s.getpeername()[0]}:{s.getpeername()[1]} ended transmitting.')
                s.close()
                break

    def start(self):
        """Starts the appropriate server"""
        if self.protocol == "UDP":
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.bind((self.host, self.port))
            self.host = server_socket.getsockname()[0]
            self.port = server_socket.getsockname()[1]
            print(f'{self.protocol} server is running at {self.host}:{self.port}')
            threading.Thread(target=self.udp_handler,
                             args=(server_socket,)).start()

        if self.protocol == "TCP":
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((self.host, self.port))
            self.host = server_socket.getsockname()[0]
            self.port = server_socket.getsockname()[1]
            print(f'{self.protocol} server is running at {self.host}:{self.port}')
            server_socket.listen(1)
            while (True):
                connection_socket, client_address = server_socket.accept()
                threading.Thread(target=self.tcp_handler,
                                 args=(connection_socket,)).start()


if __name__ == "__main__":
    udp = Server(protocol="UDP", port=23450)
    udp.start()

    tcp = Server(protocol="TCP", port=23451)
    tcp.start()
