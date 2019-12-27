from flask_bcrypt import generate_password_hash
from models.stripe import Stripe, db
import json
from sqlalchemy.exc import IntegrityError
import traceback

class StripeAccess():
    def __init__(self):
        self.db = db
        self.Stripe = Stripe

    def get_stripe(self, user_id=None, subscription_id=None):
        if user_id != None:
            return self.Stripe.query.filter_by(user_id=user_id).first()
        elif subscription_id != None:
            return self.Stripe.query.filter_by(subscription_id=subscription_id).first()

