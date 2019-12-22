import sys
import json
import os
import stripe
from flask import request
import traceback

base_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..'))
sys.path.append(base_dir)

# Import all the things
from backend import app, db, User, Notifications, Stripe
from action.notification_action import NotificationAction

action = NotificationAction(db, app, User, Notifications, Stripe)

@app.route("/notification_read", methods=["PUT"])
def notification_read():
    try:
        data = request.get_json(force=True)
        noti_id = data['noti_id']

        notifications = Notifications.query.filter_by(id=noti_id).first()
        notifications.isRead = True

        db.session.commit()

        return json.dumps({'message':''}), 200
    except Exception as ex:
        return json.dumps({'message':'Unknown error, we apologize'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['NOTIFICATION_PORT'])