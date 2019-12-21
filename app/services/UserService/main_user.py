import sys
import os
import stripe
from flask import request
from flask_login import login_required, current_user

base_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..'))
sys.path.append(base_dir)

# Import all the things
from backend import app, db, User, Notifications, csrf
from action.user_action import UserAction

action = UserAction(db, app, User, Notifications)

if __name__ == '__main__':
    app.run(host='0.0.0.0')