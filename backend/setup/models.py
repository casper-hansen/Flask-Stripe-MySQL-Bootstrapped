from flask_login import UserMixin
from backend.setup import db
from sqlalchemy import Column, Integer, DateTime, String, Boolean
from sqlalchemy.sql import func

class User(UserMixin, db.Model):
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), unique=False, nullable=False)
    created_date = Column(DateTime, server_default=func.now())
    subscription_active = Column(Boolean, default=False, nullable=False)
    subscription_id = Column(String(256), unique=False)
    customer_id = Column(String(256), unique=False)
    subscription_cancelled_at = Column(Integer, unique=False)
    is_authenticated = True

    def __repr__(self):
        return 'id: '.join([str(id)])