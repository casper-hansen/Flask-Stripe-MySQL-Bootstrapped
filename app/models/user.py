from backend import db
from flask_login import UserMixin
from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship,backref

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), unique=False, nullable=False)
    name = Column(String(50), nullable=False)
    created_date = Column(DateTime, server_default=func.now())
    
    is_authenticated = True

    def __repr__(self):
        return 'id: '.join([str(id)])

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)