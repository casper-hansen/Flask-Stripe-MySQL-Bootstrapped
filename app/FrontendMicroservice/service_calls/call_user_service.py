from flask import Flask, Blueprint, request, current_app
from flask_login import login_user
from notifications import Notifications, db
from user import User
import json, requests

user_api = Blueprint('user_api', __name__)

@user_api.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(force=True)

    r = requests.post('http://' + current_app.config['BASE_URL'] + ':' +  current_app.config['USER_PORT'] + '/signup', json=data)
    
    return r.text, r.status_code

@user_api.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)

    r = requests.post('http://' + current_app.config['BASE_URL'] + ':' +  current_app.config['USER_PORT'] + '/login', json=data)

    if r.status_code == 200:
        user = get_user(data['email'])
        if user == None:
            return 'User not found', 404

        login_user(user, remember=True)

    return r.text, r.status_code

def get_user(email):
    r = requests.get('http://' + current_app.config['BASE_URL'] + ':' +  current_app.config['USER_PORT'] + '/getuser/email/' + email)

    if r.status_code == 200:
        user_dict = json.loads(r.text)
        return User(**user_dict)
    else:
        return None