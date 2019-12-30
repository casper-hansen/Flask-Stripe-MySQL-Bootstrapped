from flask import Flask, current_app, jsonify
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
import stripe, json, sys, os, traceback, time
from datetime import timedelta, datetime
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

    def get_notifications(self, user_id):
        try:
            notification = db_access.get_notification(user_id=user_id, get_all=True, is_read=[False, False], as_dict=True)

            if notification != None:
                return jsonify(notification), 200
            else:
                return json.dumps({'message':'Notification was not found'}), 404
        except Exception as ex:
            stacktrace = traceback.format_exc()
            print(stacktrace)
            return json.dumps({'message':'Unknown error, we apologize'}), 500

    def get_unread_notifications(self, user_id):
        try:
            notification = db_access.get_notification(user_id=user_id, is_read=[True, False], get_all=True, as_dict=True)

            if notification != None:
                return jsonify(notification), 200
            else:
                return json.dumps({'message':'Notification was not found'}), 404
        except Exception as ex:
            stacktrace = traceback.format_exc()
            print(stacktrace)
            return json.dumps({'message':'Unknown error, we apologize'}), 500