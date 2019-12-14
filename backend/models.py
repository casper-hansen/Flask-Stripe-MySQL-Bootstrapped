from flask_login import UserMixin
from backend.setup import db
from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship,backref

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), unique=False, nullable=False)
    created_date = Column(DateTime, server_default=func.now())
    
    is_authenticated = True

    def __repr__(self):
        return 'id: '.join([str(id)])

class Stripe(db.Model):
    __tablename__ = 'stripe'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), unique=False, nullable=False)
    user = relationship("User", backref=backref("user", uselist=False))

    subscription_id = Column(String(256), unique=False, nullable=False)
    customer_id = Column(String(256), unique=False, nullable=False)
    payment_method_id = Column(String(256), unique=False, nullable=True)
    subscription_active = Column(Boolean, default=False)
    amount = Column(Integer, unique=False)
    current_period_start = Column(Integer, unique=False)
    current_period_end = Column(Integer, unique=False)
    subscription_cancelled_at = Column(Integer, unique=False)

    def __repr__(self):
        return 'id: '.join([str(id)])

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

class Notifications(db.Model):
    __tablename__  = 'notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), unique=False, nullable=False)
    #user = relationship("User", backref=backref("user_ref", uselist=False))

    color = Column(String(50))
    icon = Column(String(50))
    created_date = Column(DateTime, server_default=func.now())
    message = Column(String(500))