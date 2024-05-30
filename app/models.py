"""
Database Models for Chat Application

This script defines the SQLAlchemy ORM models for the chat application, including
User and PublicMessage models. It includes relationships, schema definitions, and
basic methods for user authentication.

Imports:
    - bcrypt: For password hashing and checking
    - sqlalchemy components: Column, Integer, String, ForeignKey, declarative_base, relationship

Classes:
    - User: Represents a user with a username and password hash.
    - PublicMessage: Represents a public message with an author and message content.

Usage:
    Define the database models and use them in your application for database operations.
"""

from datetime import datetime

import bcrypt

from utils.constants import SECRET

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, relationship
from cryptography.fernet import Fernet
import base64

import os

key = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key().decode())
f = Fernet(key.encode())
Base = declarative_base()


class User(Base):
    """
    Represents a user in the chat application.

    Attributes:
        id (int): Primary key of the user.
        username (str): Unique username of the user.
        password_hash (str): Hashed password of the user.
        messages (relationship): Relationship to the PublicMessage model.

    Methods:
        __repr__: Returns a string representation of the user.
        check_password: Checks if the provided password matches the stored password hash.
    """
    __tablename__ = "users"
    __table_args__ = {"schema": "chat"}

    id: int = Column(Integer, primary_key=True)
    username: str = Column(String(50), unique=True, nullable=False)
    password_hash: str = Column(String(128), nullable=False)

    messages = relationship("PublicMessage", back_populates="author")

    def __repr__(self) -> str:
        return f"User(username='{self.username}')"

    def check_password(self, password: str) -> bool:
        """
        Check if the provided password matches the stored password hash.

        Args:
            password (str): The password to check.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))


class PublicMessage(Base):
    """
    Represents a public message in the chat application.

    Attributes:
        id (int): Primary key of the message.
        author_id (int): Foreign key linking to the User who sent the message.
        message (str): Content of the message.
        timestamp (datetime): Timestamp of when the message was created.
        author (relationship): Relationship to the User model.

    Methods:
        __repr__: Returns a string representation of the message.
    """
    __tablename__ = "messages"
    __table_args__ = {"schema": "chat"}

    id: int = Column(Integer, primary_key=True)
    author_id: int = Column(Integer, ForeignKey("chat.users.id"))
    _message: str = Column("message", String(1024), nullable=False)
    timestamp: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    author = relationship("User", back_populates="messages")

    @property
    def message(self):
        decrypted_message: str = f.decrypt(self._message.encode()).decode()
        return decrypted_message
    
    @message.setter
    def message(self, value: str):
        encrypted_message: str = f.encrypt(value.encode()).decode()
        self._message = encrypted_message

    def __repr__(self) -> str:
        return f"Author Id: {self.author_id} - Message: {self.message} - Timestamp: {self.timestamp}"
