from flask_bcrypt import generate_password_hash
from models.user import db, User
from models.notifications import Notifications
import json
from sqlalchemy.exc import IntegrityError
import traceback

class UserAccess():

    def __init__(self):
        self.db = db
        self.User = User
        self.Notifications = Notifications

    def get_user(self, id=None, email=None, as_dict=False):
        if id != None:
            user = self.User.query.filter_by(id=id).first()
        elif email != None:
            user = self.User.query.filter_by(email=email).first()

        if as_dict:
            return self.User.as_dict(user)
        else:
            return user

    def create_user(self, email, password, name):
        try:
            # Hash the password (store only the hash)
            pw_hash = generate_password_hash(password, 10)

            # Save user in database
            new_user = self.User(name=name, email=email, password_hash=pw_hash)

            # Take the row spot
            self.db.session.add(new_user)
            self.db.session.flush()

            # Make notification
            new_notification = self.Notifications(user_id=new_user.id,
                                                    color = 'success',
                                                    icon = 'check-circle',
                                                    message_preview = 'You are signed up! Thanks for joining this service.',
                                                    message = 'You have successfully signed up!')
            self.db.session.add(new_notification)

            # Commit changes
            self.db.session.commit()

            return json.dumps({'message':'/login_page'}), 200
        except IntegrityError as ex:
            stacktrace = traceback.format_exc()
            print(stacktrace)
            self.db.session.rollback()
            return json.dumps({'message':'Email already registered'}), 403
        except Exception as ex:
            stacktrace = traceback.format_exc()
            print(stacktrace)
            return json.dumps({'message':'Something went wrong'}), 401
        
