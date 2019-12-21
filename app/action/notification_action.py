from flask import Flask, current_app
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
import stripe
import json
import sys
import os
from datetime import timedelta, datetime
import traceback
import time
from flask_bcrypt import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

class NotificationAction():
    def __init__(self, db, app, User, Notifications, Stripe):
        self.User = User
        self.Notifications = Notifications
        self.Stripe = Stripe
        self.db = db
        self.app = app