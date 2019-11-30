from flask_login import UserMixin
from backend.setup import db
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.sql import func

class User(UserMixin, db.Model):
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), unique=False, nullable=False)
    created_date = Column(DateTime, server_default=func.now())
    is_authenticated = True
    is_subscribed = False

    def __repr__(self):
        return 'id: '.join([id])