from setup_app import db, app
from flask_login import UserMixin
from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship,backref

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

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)