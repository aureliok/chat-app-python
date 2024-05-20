"""
Chat Client Handler Script

This script defines a client handler class, ClientHandler, for handling communication 
with a chat server from the client side.
"""

import socket
import sys
import os

if os.name == "nt":  # For Windows
    import msvcrt


class ClientHandler:
    """
    ClientHandler class for handling communication with the chat server.

    This class provides methods for receiving and sending messages to/from the chat server.

    Attributes:
        client_socket (socket.socket): The socket object representing the client connection.
        current_input (str): The current input message from the client.
        username (str): The username or identifier for the client.

    Methods:
        receive_messages(): Continuously receive messages from the chat server
                            and display them to the client.
        send_messages(): Continuously prompt the client for messages and
                         send them to the chat server.
        end_connection(): Close the connection to the chat server.
    """

    def __init__(self, client_socket: socket.socket, username: str) -> None:
        """
        Initialize the ClientHandler instance.

        Args:
            client_socket (socket.socket): The socket object representing the client connection.
        """
        self.client_socket: socket.socket = client_socket
        self.current_input: str = ""
        self.username: str = username

    def receive_messages(self) -> None:
        """
        Receive messages from the chat server and display them to the client.
        """
        while True:
            try:
                message: str = self.client_socket.recv(1024).decode("utf-8")
                if not message:
                    break

                sys.stdout.write("\r" + " " * 80 + "\r")
                print(message)
                sys.stdout.write("You: ")
                sys.stdout.flush()
            except Exception as e:
                print(f"Connection to server lost: {e}")
                self.client_socket.close()
                break

    def send_messages(self) -> None:
        """
        Prompt the client for messages and send them to the chat server.
        """
        while True:
            self.current_input = input("You: ")
            if os.name == "nt":  # For Windows
                msvcrt.putch(b"\b" * len("You: "))  # type: ignore
            else:  # For Unix/Linux/MacOS
                sys.stdout.write("\033[F")  # Move cursor up one line
                sys.stdout.write("\033[K")  # Clear current line
            try:
                self.client_socket.send(self.current_input.encode("utf-8"))
                if self.current_input == "!exit":
                    self.end_connection()
                    break
            except Exception as e:
                print(f"Error sending message: {e}")
                self.end_connection()
                break

    def end_connection(self) -> None:
        """
        Close connection to server.
        """
        self.client_socket.close()
