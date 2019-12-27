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
from data_access.user_db import UserAccess

db_access = UserAccess()

class UserAction():
    def __init__(self, app):
        self.app = app

    def signup(self, request):
        # Get data from AJAX request
        data = request.get_json(force=True)
        
        email = data['email']
        password = data['password']
        name = data['name']

        message, status_code = db_access.create_user(email=email,
                                                    password=password,
                                                    name=name)

        return message, status_code

    def login(self, request):
        try:
            # Get data from AJAX request
            data = request.get_json(force=True)
            email = data['email']
            password = data['password']

            # Find user
            user = db_access.get_user(email=email)

            return self._check_user_data(user, password, email)
        except Exception as ex:
            stacktrace = traceback.format_exc()
            print(stacktrace)
            return json.dumps({'message':'Unknown error, we apologize'}), 500

    def _check_user_data(self, user, password, email):
        # If user exists, check if email and password matches
        if user != None:
            check_pw = check_password_hash(user.password_hash, password)
            if user.email == email and check_pw:
                return json.dumps({'message':'/dashboard'}), 200
            else:
                return json.dumps({'message':'User data incorrect'}), 401
        else:
            return json.dumps({'message':'Email not registered'}), 401