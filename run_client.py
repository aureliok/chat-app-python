"""
Module to run the chat client.
"""

import os

import requests
import app.routes.auth as auth
from classes.client.client import ChatClient
from utils.constants import URL


if __name__ == "__main__":

    # Clear the console based on the operating system
    if os.name == "nt":  # For Windows
        os.system("cls")
    else:  # For Unix/Linux/MacOS
        os.system("clear")

    chatClient: ChatClient = ChatClient()

    option: str = input("Select an option:\n[1] - Login\n[2] - Register\n")
    if option == "1":
        url: str = URL + "/login"
        username: str = input("Enter username: ")
        password: str = input("Enter password: ")
        chatClient.start(username=username, password=password, create_new_user=False)
    elif option == "2":
        url: str = URL + "/register"
        username: str = input("Enter username: ")
        password: str = input("Enter password: ")
        chatClient.start(username=username, password=password, create_new_user=True)
    else:
        raise ValueError("Invalid option, quitting application")
