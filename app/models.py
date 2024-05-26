import bcrypt

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "chat"}

    id: int = Column(Integer, primary_key=True)
    username: str = Column(String(50), unique=True, nullable=False)
    password_hash: str = Column(String(128), nullable=False)

    messages = relationship("PublicMessage", back_populates="author")

    def __repr__(self) -> str:
        return f"User(username='{self.username}')"

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))
    

class PublicMessage(Base):
    __tablename__ = "messages"
    __table_args__ = {"schema": "chat"}

    id: int = Column(Integer, primary_key=True)
    author_id: int = Column(Integer, ForeignKey("chat.users.id"))
    message: str = Column(String(1024), nullable=False)

    author = relationship("User", back_populates="messages")

    def __repr__(self) -> str:
        return f"Author Id: {self.author_id} - Message: {self.message}"
