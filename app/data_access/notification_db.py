from models.notifications import Notifications, db

class NotificationAccess():
    def __init__(self):
        self.db = db
        self.Notification = Notifications

    def get_stripe(self, noti_id=None, get_all=False):
        if noti_id != None:
            noti_obj = self.Notification.query.filter_by(id=noti_id)

        if get_all:
            return noti_obj.all()
        else:
            return noti_obj.first()
    
    def create_notification(self, notification_dict):
        notification_row = self.Notification(**notification_dict)
        self.db.session.add(notification_row)
        self.db.session.commit()
    
    def update_stripe_by_dict(self, noti_id, noti_obj):
        notification_row = self.Notification.query.filter_by(id=noti_id).first()
        notification_row.update(**noti_obj)
        self.db.session.commit()