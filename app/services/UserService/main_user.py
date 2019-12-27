import sys
import json
import os
import stripe
from flask import request

from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

base_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..'))
sys.path.append(base_dir)

# Import all the things
from setup_app import app, User, Notifications, Stripe
from action.user_action import UserAction

action = UserAction(app)

@app.route("/signup", methods=["POST"])
def signup():
    '''
        Endpoint for signing up a user and saving in the database.

        Parameters
        ----------
        request : JSON data
            Has to contain the email and password for a user.

        Returns (JSON)
        -------
        {
            message : string 
                Renders a URL to the login page on success. Gives error message otherwise.
        }
    '''
    return action.signup(request)

@app.route("/login", methods=["POST"])
def login():
    '''
        Endpoint for logging in.

        Parameters
        ----------
        request : JSON data
            Has to contain the email and password for a user.

        Returns (JSON)
        -------
        {
            message : string 
                Renders a URL to the dashboard on success. Gives error message otherwise.
        }
    '''
    return action.login(request)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['USER_PORT'])