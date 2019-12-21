from flask import Flask, Blueprint, request
from models.notifications import Notifications, db
import json, requests

user_api = Blueprint('user_api', __name__)

@user_api.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(force=True)

    r = requests.post('http://localhost:5003/signup', json=data)

    return r.text, r.status_code

@user_api.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)

    r = requests.post('http://localhost:5003/login', json=data)

    #if r.status_code == 200:
    #    login_user(user, remember=True)

    return r.text, r.status_code