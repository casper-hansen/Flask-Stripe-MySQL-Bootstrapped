import sys
import json
import os
import stripe
from flask import request
import traceback

base_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..'))
sys.path.append(base_dir)

# Import all the things
from setup_app import app
from action.notification_action import NotificationAction

action = NotificationAction(app)

@app.route("/notification_read", methods=["PUT"])
def notification_read():
    return action.notification_read(request)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['NOTIFICATION_PORT'])