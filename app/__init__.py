from flask import Flask
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from utils.constants import SECRET
from app.models import Base

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET
app.config["DATABASE_URI"] = "postgresql://psql_user:postgres@localhost:5432/chat_app"

engine = create_engine(app.config["DATABASE_URI"])

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

from .routes import auth