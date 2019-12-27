from models.notifications import Notifications, db

class NotificationAccess():
    def __init__(self):
        self.db = db
        self.Notification = Notifications

    def get_notification(self, user_id=None, noti_id=None, get_all=False, as_dict=False):
        if user_id != None:
            noti_obj = self.Notification.query.filter_by(user_id=user_id, isRead=False).order_by(self.Notification.created_date.desc())
        elif noti_id != None:
            noti_obj = self.Notification.query.filter_by(id=noti_id)

        if get_all:
            noti_obj = noti_obj.all()
        else:
            noti_obj = noti_obj.first()

        if as_dict and noti_obj != None:
            return [self.Notification.as_dict(noti) for noti in noti_obj]
        
        return noti_obj
    
    def create_notification(self, notification_dict):
        notification_row = self.Notification(**notification_dict)
        self.db.session.add(notification_row)
        self.db.session.commit()
    
    def update_notification_by_dict(self, noti_id, noti_obj):
        notification_row = self.Notification.query.filter_by(id=noti_id).first()
        notification_row.update(**noti_obj)
        self.db.session.commit()