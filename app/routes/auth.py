import bcrypt
import jwt
from datetime import datetime, timezone, timedelta

from flask import request, jsonify, Response
from app.models import User
from typing import Dict, Tuple, Optional
from utils.constants import SECRET
from app import app, Session


@app.route("/register", methods=["POST"])
def register() -> Tuple[Response, int]:
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
            {"user_id": user.id, "username": username, "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=10)},
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        return jsonify({"message": "Login successful", "token": token}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 400
