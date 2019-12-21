from flask import Flask, current_app
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
import stripe
import json
import sys
import os
from datetime import timedelta, datetime
import traceback

class UserAction():
    def __init__(self, db, app, User, Notifications):
        self.User = User
        self.Notifications = Notifications
        self.db = db
        self.app = app