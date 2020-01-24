from notifications import Notifications, db

class NotificationAccess():
    def __init__(self):
        self.db = db
        self.Notification = Notifications

    def get_notification(self, user_id=None, noti_id=None, is_read=[False, False], get_all=False, as_dict=False):
        '''
            is_read[0] : if you want to use isRead as a filter
            is_read[1] : if you want isRead to be true or false
        '''
        if user_id != None:
            if is_read[0]:
                noti_obj = self.Notification.query.filter_by(user_id=user_id, isRead=is_read[1]).order_by(self.Notification.created_date.desc())
            else:
               noti_obj = self.Notification.query.filter_by(user_id=user_id).order_by(self.Notification.created_date.desc())
        elif noti_id != None:
            if is_read[0]:
                noti_obj = self.Notification.query.filter_by(id=noti_id, isRead=is_read[1])
            else:
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