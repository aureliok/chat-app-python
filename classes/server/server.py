"""
Chat Server Script

This script defines a simple chat server implementation using the ChatServer class.
The server listens for incoming connections from clients and facilitates communication
between them.
"""

import socket
import threading
from typing import List, Tuple
from datetime import datetime

TIMESTAMP_FORMAT = "%d/%m/%Y %H:%M:%S"


class ChatServer:
    """
    A simple chat server implementation.

    This class represents a basic chat server that listens for incoming connections
    from clients and facilitates communication between them.

    Attributes:
        host (str): The IP address or hostname of the server. Default is '127.0.0.1'.
        port (int): The port number on which the server listens for connections. Default is 9999.

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
        self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.clients: List[socket.socket] = []

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
                self.clients.append(client_socket)
                threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()
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
                sender_info: str = f"{client_socket.getpeername()}"
                message_with_sender = f"{sender_info} [{datetime.now().strftime(TIMESTAMP_FORMAT)}]: {message}"
                if not message:
                    break
                print(f"{addr} says: {message}")
                self.broadcast(message_with_sender)

            except OSError as e:
                if e.errno == 9:
                    print("Client closed the connection")
                else:
                    print(f"Error receiving message from {addr}: {e}")

                break
            except Exception as e:
                print(f"Error handling client {addr}: {e}")
                break

        self.clients.remove(client_socket)
        client_socket.close()

    def remove_client(self, client_socket: socket.socket) -> None:
        """
        Remove a client from the list of active clients.

        Args:
            client_socket (socket.socket):
                The socket object representing the client connection to be removed.
        """
        if client_socket in self.clients:
            self.clients.remove(client_socket)

    def broadcast(self, message: str) -> None:
        """
        Broadcast a message to all connected clients.

        Args:
            message (str): The message to be broadcasted.
        """
        print(f"Broadcasting to {len(self.clients)} users")
        for client in self.clients:
            try:
                client.send(message.encode("utf-8"))
            except Exception as e:
                print(f"Error broadcasting message to {client.getsockname()} : {e}")
                client.close()
                self.clients.remove(client)
                print(f"Client {client.getsockname()} removed")
