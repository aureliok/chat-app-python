import socket
import threading
import time
from typing import Tuple
import pytest
from classes.client.client import ChatClient
from classes.client.client_handler import ClientHandler
from classes.server.server import ChatServer


@pytest.fixture
def chat_server() -> Tuple[ChatServer, int]:
    """
    Fixture to create and return a ChatServer instance bound to an available port.

    Returns:
        Tuple[ChatServer, int]: The ChatServer instance and the port it is bound to.
    """
    server: ChatServer = ChatServer(port=0)
    server.port = server.server_socket.getsockname()[1]
    return server, server.port


def run_server_in_thread(chat_server: ChatServer) -> None:
    """
    Run the ChatServer in a separate thread.

    Args:
        chat_server (ChatServer): The ChatServer instance to run.
    """
    server_thread = threading.Thread(target=chat_server.start, daemon=True)
    server_thread.start()
    time.sleep(1)


def test_chat_client_initialization(chat_server: Tuple[ChatServer, int]) -> None:
    """
    Test the initialization of a ChatClient instance.

    Args:
        chat_server (Tuple[ChatServer, int]): A tuple containing a ChatServer instance 
                                              and the port number on which the server 
                                              is running.
    """
    server, port = chat_server
    run_server_in_thread(server)

    chat_client: ChatClient = ChatClient(server.host, server.port)

    assert chat_client.host == "127.0.0.1"
    assert chat_client.port == port
    assert isinstance(chat_client.client_socket, socket.socket)
    assert isinstance(chat_client.client_handler, ClientHandler)
