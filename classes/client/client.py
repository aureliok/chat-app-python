"""
Chat Client Script

This script defines a simple chat client implementation using the ChatClient class.
The client connects to a chat server and facilitates communication with other clients.
"""

import socket
import threading
from .client_handler import ClientHandler


class ChatClient:
    """
    A simple chat client implementation.

    This class represents a basic chat client that connects to a chat server
    and facilitates communication with other clients.

    Attributes:
        host (str): The IP address or hostname of the chat server. Default is '127.0.0.1'.
        port (int): The port number on which the chat server listens for connections.
                    Default is 9999.

    Methods:
        start(): Start the chat client, connecting to the chat server and initiating
                 message sending/receiving.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 9999):
        """
        Initialize the ChatClient instance.

        Args:
            host (str): The IP address or hostname of the chat server. Default is '127.0.0.1'.
            port (int): The port number on which the chat server listens for connections.
                        Default is 9999.
        """
        self.host: str = host
        self.port: int = port
        self.client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.client_handler: ClientHandler = ClientHandler(self.client_socket)

    def start(self) -> None:
        """
        Start the chat client.

        Connects to the chat server and initiates message sending/receiving by starting
        separate threads for sending and receiving messages.
        """
        threading.Thread(target=self.client_handler.receive_messages).start()
        self.client_handler.send_messages()
        print(f"Welcome {self.client_socket.getsockname()}!")
