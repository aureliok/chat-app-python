"""
Chat Server Script

This script defines a simple chat server implementation using the ChatServer class.
The server listens for incoming connections from clients and facilitates communication
between them.
"""

import socket
import threading
from typing import Tuple, Dict, List, Optional
from datetime import datetime
from app.models import PublicMessage, User

import jwt
from utils.constants import SECRET

TIMESTAMP_FORMAT: str = "%d/%m/%Y %H:%M:%S"


class ChatServer:
    """
    A simple chat server implementation.

    This class represents a basic chat server that listens for incoming connections
    from clients and facilitates communication between them.

    Attributes:
        host (str): The IP address or hostname of the server. Default is '127.0.0.1'.
        port (int): The port number on which the server listens for connections. 
                    Default is 9999.

    Methods:
        start(): Start the chat server and listen for incoming connections.
        handle_client(client_socket: socket.socket, addr: Tuple[str, int]):
            Handle communication with a connected client.
        remove_client(client_socket: socket.socket):
            Remove a client from the list of active clients.
        broadcast(message: str, current_client: socket.socket):
            Broadcast a message to all connected clients except the sender.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 9999) -> None:
        """
        Initialize the ChatServer instance.

        Args:
            host (str): The IP address or hostname of the server. Default is '127.0.0.1'.
            port (int): The port number on which the server listens for connections.
                        Default is 9999.
        """

        self.host: str = host
        self.port: int = port
        self.secret_key: str = SECRET
        self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.clients: Dict[socket.socket, (str, int)] = {}

        print(f"Server listening on {self.host}:{self.port}")

    def start(self) -> None:
        """
        Start the chat server and listen for incoming connections.
        """
        while True:
            try:
                client_socket: socket.socket
                addr: Tuple[str, int]
                client_socket, addr = self.server_socket.accept()
                token: str = client_socket.recv(1024).decode("utf-8")
                client_username, client_id = self.verify_token(token)
                if client_username:
                    self.clients[client_socket] = (client_username, client_id)
                    self.broadcast(f"{client_username} entered the chat!")
                    threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()
                else:
                    client_socket.close()
            except Exception as e:
                print(f"Error accepting connection: {e}")

    def handle_client(self, client_socket: socket.socket, addr: Tuple[str, int]) -> None:
        """
        Handle communication with a connected client.

        Args:
            client_socket (socket.socket): The socket object representing the client connection.
            addr (Tuple[str, int]): The address (IP, port) of the connected client.
        """
        print(f"New connection from {addr}")
        while True:
            try:
                message: str = client_socket.recv(1024).decode("utf-8")
                if message == "!exit":
                    self.remove_client(client_socket)
                    break
                elif message == "!who":
                    self.show_online_users(client_socket)
                    continue
                sender_info: str = f"{self.clients[client_socket][0]}"
                message_with_sender = (
                    f"{sender_info} [{datetime.now().strftime(TIMESTAMP_FORMAT)}]: {message}"
                )
                if not message:
                    break
                print(f"{addr} says: {message}")
                self.broadcast(message_with_sender)
                self.store_message_on_database(message, client_socket)

            except OSError as e:
                if e.errno == 9:
                    print("Client closed the connection")
                else:
                    print(f"Error receiving message from {addr}: {e}")

                break
            except Exception as e:
                print(f"Error handling client {addr}: {e}")
                break

        self.remove_client(client_socket)
        client_socket.close()

    def remove_client(self, client_socket: socket.socket) -> None:
        """
        Remove a client from the list of active clients.

        Args:
            client_socket (socket.socket):
                The socket object representing the client connection to be removed.
        """
        if client_socket in self.clients:
            username: str = self.clients.pop(client_socket)
            self.broadcast(f"{username} disconnected")

    def broadcast(self, message: str, client_socket: Optional[socket.socket] = None) -> None:
        """
        Broadcast a message to all connected clients.

        Args:
            message (str): The message to be broadcasted.
        """
        clients_dict = dict(self.clients)
        for client, user_info in clients_dict.items():
            if client_socket and client != client_socket:
                continue
            try:
                username, _ = user_info
                client.send(message.encode("utf-8"))
            except Exception as e:
                print(f"Error broadcasting message to {username} : {e}")
                self.remove_client(client)
                client.close()

    def show_online_users(self, client_socket: socket.socket) -> None:
        """
        Send the list of online users to the requesting client.

        Args:
            client_socket (socket.socket): The socket object representing the client that requested the list.
        """
        users: List[str] = [username for username, user_id in self.clients.values()]
        users_online: str = str(len(users)) + " USERS ONLINE:\n" + "\n".join(users)
        print(users_online)
        self.broadcast(users_online, client_socket)

    def print_active_threads(self) -> None:
        """
        Print a list of all active threads.
        """
        threads = threading.enumerate()
        print(f"Active threads ({len(threads)}):")
        for thread in threads:
            print(f"  - {thread.name}")

    def store_message_on_database(self, message: str, client_socket: socket.socket) -> None:
        pass

    def verify_token(self, token: str) -> Optional[str]:
        """
        Verify the provided JWT token and extract the username.

        This method decodes the provided JWT token using the secret key.
        If the token is valid, it returns the username from the decoded token.
        If the token is expired or invalid, it prints an appropriate message and returns None.

        Args:
            token (str): The JWT token to be verified.

        Returns:
            Optional[str]: The username if the token is valid, None otherwise.

        Raises:
            jwt.ExpiredSignatureError: If the token has expired.
            jwt.InvalidTokenError: If the token is invalid.
        """
        try:
            decoded_token = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return decoded_token.get("username"), decoded_token.get("id")
        except jwt.ExpiredSignatureError:
            print("Token has expired")
        except jwt.InvalidTokenError:
            print("Invalid token")
        return None, None
