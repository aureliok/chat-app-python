"""
Module to run the chat server.
"""

from classes.server.server import ChatServer

if __name__ == "__main__":
    chatServer: ChatServer = ChatServer()
    chatServer.start()
