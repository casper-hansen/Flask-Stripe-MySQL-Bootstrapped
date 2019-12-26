from flask_bcrypt import generate_password_hash
from models.user import db, User
from models.notifications import Notifications

class UserAccess():

    def __init__(self):
        self.db = db
        self.User = User
        self.Notifications = Notifications

    def create_user(self, email, password, name):
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
