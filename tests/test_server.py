"""
Unit tests for the ChatServer class.

This module contains tests for the following functionalities:
- Initialization of the ChatServer.
- Starting the ChatServer and handling client connections.
- User connection and disconnection.
- Listing online users.

The tests utilize the pytest framework and fixtures to set up and tear down the required resources.
"""

import socket
import threading
import time
from datetime import datetime, timezone, timedelta
from typing import Tuple
import jwt
import bcrypt
import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from classes.server.server import ChatServer
from app import app
from app.models import User, PublicMessage, Base


@pytest.fixture(scope="session")
def testing_engine():
    """Provides the testing database engine for tests."""

    app.config["TESTING_DATABASE_URI"] = (
        "postgresql://psql_user:postgres@localhost:5432/test_chat_app"
    )
    engine = create_engine(app.config["TESTING_DATABASE_URI"])
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(testing_engine):
    """Provides a database session scoped to each test.

    - Creates a new database session for each test using `testing_engine`.
    - Rolls back the session after each test to ensure data isolation.
    - Closes the session to release resources properly.
    """

    Session = sessionmaker(bind=testing_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def auth_token(db_session):
    """Provides an authentication token for testing authenticated routes.

    - Creates a user object directly within the fixture (instead of using an API call).
    - Adds the user to the `db_session` for persistence during the test.
    - Logs in the user using a mock or placeholder logic (replace with actual login implementation).
    - Yields the authentication token to tests that require it.
    """
    password: str = "testpassword"
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    hashed_password_str: str = hashed_password.decode("utf-8")
    user = User(username="Tester", password_hash=hashed_password_str)
    db_session.add(user)

    token: str = jwt.encode(
        {"username": "Tester", "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=10)},
        app.config["SECRET_KEY"],
        algorithm="HS256",
    )

    return token


@pytest.fixture
def auth_token2(db_session):
    """Provides an authentication token for testing authenticated routes.

    - Creates a user object directly within the fixture (instead of using an API call).
    - Adds the user to the `db_session` for persistence during the test.
    - Logs in the user using a mock or placeholder logic (replace with actual login implementation).
    - Yields the authentication token to tests that require it.
    """
    password: str = "testpassword"
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    hashed_password_str: str = hashed_password.decode("utf-8")
    user = User(username="Tester2", password_hash=hashed_password_str)
    db_session.add(user)

    token: str = jwt.encode(
        {"username": "Tester2", "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=10)},
        app.config["SECRET_KEY"],
        algorithm="HS256",
    )
    return token


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


@pytest.fixture
def client_socket():
    """
    Fixture to create and return a client socket.

    Yields:
        socket.socket: The client socket.
    """
    s: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    yield s
    s.close()


@pytest.fixture
def other_socket():
    """
    Fixture to create and return another client socket.

    Yields:
        socket.socket: The other client socket.
    """
    s: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    yield s
    s.close()


def run_server_in_thread(chat_server: ChatServer) -> None:
    """
    Run the ChatServer in a separate thread.

    Args:
        chat_server (ChatServer): The ChatServer instance to run.
    """
    server_thread = threading.Thread(target=chat_server.start, daemon=True)
    server_thread.start()
    time.sleep(1)


def test_chat_server_initialization(chat_server: Tuple[ChatServer, int]) -> None:
    """
    Test the initialization of the ChatServer.

    Args:
        chat_server (Tuple[ChatServer, int]): The ChatServer instance and the port it is bound to.
    """
    server, port = chat_server
    assert server.host == "127.0.0.1"
    assert server.port == port
    assert isinstance(server.clients, dict)


def test_chat_server_start(
    chat_server: Tuple[ChatServer, int], client_socket: socket.socket, auth_token: str
) -> None:
    """
    Test the start of the ChatServer and client connection.

    Args:
        chat_server (Tuple[ChatServer, int]): The ChatServer instance and the port it is bound to.
        client_socket (socket.socket): The client socket.
    """
    server, port = chat_server
    run_server_in_thread(server)
    client_socket.connect((server.host, port))

    client_socket.send(auth_token.encode("utf-8"))
    response: str = client_socket.recv(1024).decode("utf-8")

    assert response == "Tester entered the chat!"


def test_chat_server_user_connected(
    chat_server: Tuple[ChatServer, int], client_socket: socket.socket, auth_token: str
) -> None:
    """
    Test if a user successfully connects to the ChatServer.

    Args:
        chat_server (Tuple[ChatServer, int]): The ChatServer instance and the port it is bound to.
        client_socket (socket.socket): The client socket.
    """
    server, port = chat_server
    run_server_in_thread(server)
    client_socket.connect((server.host, port))

    client_socket.send(auth_token.encode("utf-8"))
    _ = client_socket.recv(1024).decode("utf-8")
    time.sleep(1)

    assert len(server.clients.keys()) == 1
    assert "Tester" in [user_data[0] for user_data in server.clients.values()]


def test_chat_server_user_disconnected(
    chat_server: Tuple[ChatServer, int], client_socket: socket.socket, auth_token: str
) -> None:
    """
    Test if a user successfully disconnects from the ChatServer using the "!exit" command.

    Args:
        chat_server (Tuple[ChatServer, int]): The ChatServer instance and the port it is bound to.
        client_socket (socket.socket): The client socket.
    """
    server, port = chat_server
    run_server_in_thread(server)
    client_socket.connect((server.host, port))
    client_socket.send(auth_token.encode("utf-8"))
    _ = client_socket.recv(1024).decode("utf-8")

    client_socket.send("!exit".encode("utf-8"))
    time.sleep(1)

    assert len(server.clients.keys()) == 0
    assert "Tester" not in [user_data[0] for user_data in server.clients.values()]


def test_chat_server_user_disconnected_forced(
    chat_server: Tuple[ChatServer, int], client_socket: socket.socket, auth_token: str
) -> None:
    """
    Test if a user is successfully removed from the ChatServer when the
    connection is closed forcibly.

    Args:
        chat_server (Tuple[ChatServer, int]): The ChatServer instance and the port it is bound to.
        client_socket (socket.socket): The client socket.
    """
    server, port = chat_server
    run_server_in_thread(server)
    client_socket.connect((server.host, port))
    client_socket.send(auth_token.encode("utf-8"))
    _ = client_socket.recv(1024).decode("utf-8")

    client_socket.close()
    time.sleep(1)

    assert len(server.clients.keys()) == 0
    assert "Tester" not in server.clients.values()


def test_chat_server_users_online(
    chat_server: Tuple[ChatServer, int],
    client_socket: socket.socket,
    other_socket: socket.socket,
    auth_token: str,
    auth_token2: str,
) -> None:
    """
    Test if the ChatServer correctly lists online users.

    Args:
        chat_server (Tuple[ChatServer, int]): The ChatServer instance and the port it is bound to.
        client_socket (socket.socket): The client socket.
        other_socket (socket.socket): Another client socket.
    """
    server, port = chat_server
    run_server_in_thread(server)
    client_socket.connect((server.host, port))
    other_socket.connect((server.host, port))
    client_socket.send(auth_token.encode("utf-8"))
    _ = client_socket.recv(1024).decode("utf-8")
    other_socket.send(auth_token2.encode("utf-8"))
    _ = client_socket.recv(1024).decode("utf-8")
    _ = other_socket.recv(1024).decode("utf-8")

    client_socket.send("!who".encode("utf-8"))
    time.sleep(1)
    response: str = client_socket.recv(1024).decode("utf-8")

    assert "2 USERS ONLINE:\nTester\nTester2" == response


def test_chat_server_message_broadcast(
    chat_server: Tuple[ChatServer, int],
    client_socket: socket.socket,
    other_socket: socket.socket,
    auth_token: str,
    auth_token2: str,
) -> None:
    """
    Test if the ChatServer correctly broadcasts messages to other users.

    Args:
        chat_server (Tuple[ChatServer, int]): The ChatServer instance and the port it is bound to.
        client_socket (socket.socket): The client socket.
        other_socket (socket.socket): Another client socket.
    """
    server, port = chat_server
    run_server_in_thread(server)
    client_socket.connect((server.host, port))
    other_socket.connect((server.host, port))
    client_socket.send(auth_token.encode("utf-8"))
    _ = client_socket.recv(1024).decode("utf-8")
    other_socket.send(auth_token2.encode("utf-8"))
    _ = client_socket.recv(1024).decode("utf-8")
    _ = other_socket.recv(1024).decode("utf-8")

    client_socket.send("Hello!".encode("utf-8"))
    time.sleep(1)
    response: str = other_socket.recv(1024).decode("utf-8")
    response_parts = response.split(": ")
    username, _ = response_parts[0].split(" [")
    message = response_parts[1]

    assert "Hello!" == message
    assert "Tester" == username
