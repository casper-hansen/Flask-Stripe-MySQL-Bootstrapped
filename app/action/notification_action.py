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
from data_access.notification_db import NotificationAccess

db_access = NotificationAccess()

class NotificationAction():
    def __init__(self, app):
        self.app = app
    
    def notification_read(self, request):
        try:
            data = request.get_json(force=True)
            noti_id = data['noti_id']

            notification = db_access.get_notification(noti_id=noti_id)

            notification_update = dict(isRead=True)
            db_access.update_notification_by_dict(notification.id, notification_update)

            return json.dumps({'message':''}), 200
        except Exception as ex:
            stacktrace = traceback.format_exc()
            print(stacktrace)
            return json.dumps({'message':'Unknown error, we apologize'}), 500