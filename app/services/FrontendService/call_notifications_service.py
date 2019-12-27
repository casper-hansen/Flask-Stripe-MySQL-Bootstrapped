from flask import Flask, Blueprint, request
from models.notifications import Notifications, db
from flask_login import current_user, login_required
import json, requests

notification_api = Blueprint('notification_api', __name__)

@notification_api.route("/notification_read", methods=["PUT"])
@login_required
def notification_read():
    data = request.get_json(force=True)

    r = requests.put('http://127.0.0.1:5002/notification_read', json=data)

    return r.text, r.status_code