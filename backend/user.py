from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, email, password):
        self.id = id
        self.email = email
        self.password = password
        
    def __repr__(self):
        return ''.join([self.id, '/', self.email, '/', self.password])