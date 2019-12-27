import sys
import json
import os
import stripe
from flask import request

from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

base_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..'))
sys.path.append(base_dir)

# Import all the things
from setup_app import app
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

@app.route("/getuser/<user_id>", methods=["GET"])
def get_user_by_user_id(user_id):
    '''
        Endpoint for getting a user by providing a user id.

        Parameters
        ----------
        request : JSON data
            Has to contain the user id.

        Returns (JSON)
        -------
        {
            message : string 
                Returns the user object
        }
    '''
    return action.get_user_by_user_id(user_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['USER_PORT'])