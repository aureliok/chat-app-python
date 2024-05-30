"""
Chat Client Script

This script defines a simple chat client implementation using the ChatClient class.
The client connects to a chat server and facilitates communication with other clients.
"""

import socket
import threading
import requests
from utils.constants import URL
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

    def __init__(self, host: str = "127.0.0.1", port: int = 9999) -> None:
        """
        Initialize the ChatClient instance.

        Args:
            host (str): The IP address or hostname of the chat server. Default is '127.0.0.1'.
            port (int): The port number on which the chat server listens for connections.
                        Default is 9999.
        """
        self.host: str = host
        self.port: int = port
        self.auth_url: str = URL
        self.client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username: str = ""
        self.password: str = ""
        self.client_socket.connect((self.host, self.port))
        self.token: str = ""
        self.client_handler: ClientHandler = ClientHandler(self.client_socket, self.username)

    def authenticate(self) -> None:
        """
        Authenticate the user with the authentication service.

        This method sends a POST request to the login endpoint with the username and password.
        If the authentication is successful, it stores the received token in the `self.token` attribute.
        Otherwise, it raises an exception indicating that authentication failed.

        Raises:
            Exception: If the authentication request fails (e.g., invalid credentials).
        """
        response = requests.post(
            self.auth_url + "/login", json={"username": self.username, "password": self.password}
        )
        if response.status_code == 200:
            self.token = response.json().get("token")
            print(self.token)
        else:
            raise Exception("Authentication failed")

    def create_user(self) -> None:
        """
        Create a new user with the authentication service and authenticate the user.

        This method sends a POST request to the register endpoint with the username and password.
        If the user creation is successful, it calls the `authenticate` method to log in the user
        and obtain a token. If the user creation fails, it raises an exception.

        Raises:
            Exception: If the user creation request fails (e.g., username already taken).
        """
        response = requests.post(
            self.auth_url + "/register", json={"username": self.username, "password": self.password}
        )
        if response.status_code == 201:
            self.authenticate()
        else:
            raise Exception("User creation failed")

    def start(self, username: str, password: str, create_new_user: bool = False) -> None:
        """
        Start the chat client.

        Connects to the chat server and initiates message sending/receiving by starting
        separate threads for sending and receiving messages.
        """
        self.username = username
        self.password = password

        if create_new_user:
            self.create_user()
        else:
            self.authenticate()

        self.client_socket.send(self.token.encode("utf-8"))
        threading.Thread(target=self.client_handler.receive_messages).start()
        self.client_handler.send_messages()
