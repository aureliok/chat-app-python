"""
Module to run the chat client.
"""

import os
from classes.client.client import ChatClient


if __name__ == "__main__":

    # Clear the console based on the operating system
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For Unix/Linux/MacOS
        os.system('clear')

    chatClient: ChatClient = ChatClient()
    chatClient.start()
