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

class UserAction():
    def __init__(self, db, app, User, Notifications, Stripe):
        self.User = User
        self.Notifications = Notifications
        self.Stripe = Stripe
        self.db = db
        self.app = app

    def signup(self, request):
        try:
            # Get data from AJAX request
            data = request.get_json(force=True)
            
            email = data['email']
            password = data['password']
            name = data['name']

            # Hash the password (store only the hash)
            pw_hash = generate_password_hash(password, 10)

            # Save user in database
            new_user = self.User(name=name, email=email, password_hash=pw_hash)

            # Take the row spot
            self.db.session.add(new_user)
            self.db.session.flush()

            # Make notification
            new_notification = self.Notifications(user_id=new_user.id,
                                                  color = 'success',
                                                  icon = 'check-circle',
                                                  message_preview = 'You are signed up! Thanks for joining this service.',
                                                  message = 'You have successfully signed up!')
            self.db.session.add(new_notification)

            # Commit changes
            self.db.session.commit()

            return json.dumps({'message':'/login_page'}), 200
        except IntegrityError as ex:
            self.db.session.rollback()
            return json.dumps({'message':'Email already registered'}), 403
        except Exception as ex:
            stacktrace = traceback.format_exc()
            print(stacktrace)
            return json.dumps({'message':'Something went wrong'}), 401

    def login(self, request):
        try:
            # Get data from AJAX request
            data = request.get_json(force=True)
            email = data['email']
            password = data['password']

            # Find user
            user = self.User.query.filter_by(email=email).first()

            # If user exists, check if email and password matches
            if user != None:
                check_pw = check_password_hash(user.password_hash, password)
                if user.email == email and check_pw:
                    return json.dumps({'message':'/dashboard'}), 200
                else:
                    return json.dumps({'message':'User data incorrect'}), 401
            else:
                return json.dumps({'message':'Email not registered'}), 401
        except Exception as ex:
            stacktrace = traceback.format_exc()
            print(stacktrace)
            return json.dumps({'message':'Unknown error, we apologize'}), 500