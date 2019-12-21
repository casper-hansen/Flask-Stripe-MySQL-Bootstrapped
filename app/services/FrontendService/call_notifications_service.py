from flask import Flask, Blueprint, request
from models.notifications import Notifications, db
import json, requests

notification_api = Blueprint('notification_api', __name__)

@notification_api.route("/notification_read", methods=["PUT"])
def notification_read():
    data = request.get_json(force=True)

    r = requests.put('http://localhost:5002/notification_read', json=data)

    return r.text, r.status_code