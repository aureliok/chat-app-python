"""
Flask Route Handlers for User Authentication

This script defines the Flask route handlers for user registration and login,
utilizing bcrypt for password hashing and JWT for token generation.

Imports:
    - bcrypt: For password hashing and checking
    - jwt: For JSON Web Token encoding
    - datetime, timezone, timedelta: For handling date and time
    - flask components: request, jsonify, Response
    - app.models: User model
    - typing: Dict, Tuple, Optional for type hinting
    - utils.constants: SECRET key for JWT
    - app: Flask application and SQLAlchemy session

Routes:
    - /register: Handles user registration
    - /login: Handles user login

Usage:
    Add these routes to the Flask application to enable user authentication.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Tuple, Optional
import bcrypt
import jwt
from flask import request, jsonify, Response
from app.models import User
from app import app, Session


@app.route("/register", methods=["POST"])
def register() -> Tuple[Response, int]:
    """
    Register a new user.

    This route handles the registration of a new user by accepting a JSON
    payload with a username and password, hashing the password, and storing
    the user in the database.

    Returns:
        Tuple[Response, int]: JSON response indicating success or failure and the HTTP status code.
    """
    data: Optional[Dict[str, str]] = request.json
    if data is not None:
        username: str = data.get("username", "")
        password: str = data.get("password", "")
    else:
        username = ""
        password = ""

    if not username or not password:
        return jsonify({"error: Username and password are both required"}), 400

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    hashed_password_str: str = hashed_password.decode("utf-8")
    print(f"Registering user: {username} with hash: {hashed_password_str}")

    session = Session()
    user = User(username=username, password_hash=hashed_password_str)
    session.add(user)
    session.commit()
    session.close()

    user2 = session.query(User).filter_by(username=username).first()
    print(f"User found: {user2.username} with stored hash: {user2.password_hash}")

    return jsonify({"message": "User registered successfully"}), 201


@app.route("/login", methods=["POST"])
def login() -> Tuple[Response, int]:
    """
    Log in an existing user.

    This route handles user login by accepting a JSON payload with a username
    and password, verifying the password, and returning a JWT token if
    authentication is successful.

    Returns:
        Tuple[Response, int]: JSON response indicating success or failure and the HTTP status code.
    """
    data: Optional[Dict[str, str]] = request.json
    if data is not None:
        username: str = data.get("username", "")
        password: str = data.get("password", "")
    else:
        username = ""
        password = ""

    if not username or not password:
        return jsonify({"error: Username and password are both required"}), 400

    session = Session()
    user: Optional[User] = session.query(User).filter_by(username=username).first()
    session.close()

    if user and user.check_password(password):
        token: str = jwt.encode(
            {
                "user_id": user.id,
                "username": username,
                "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=10),
            },
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        return jsonify({"message": "Login successful", "token": token}), 200

    return jsonify({"error": "Invalid username or password"}), 400
