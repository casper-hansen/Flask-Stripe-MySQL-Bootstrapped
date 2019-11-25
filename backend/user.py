from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), unique=False, nullable=False)
    is_subscribed = False
    is_authenticated = True

    def __repr__(self):
        return 'id: '.join([id])