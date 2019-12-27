from flask_bcrypt import generate_password_hash
from models.stripe import Stripe, db
import json
from sqlalchemy.exc import IntegrityError
import traceback
from sqlalchemy import inspect

class StripeAccess():
    def __init__(self):
        self.db = db
        self.Stripe = Stripe

    def create_stripe(self, stripe_dict):
        stripe_row = self.Stripe(**stripe_dict)
        self.db.session.add(stripe_row)
        self.db.session.commit()

    def get_stripe(self, 
                    user_id=None, subscription_id=None, customer_id=None,
                    get_all=False):
        if user_id != None:
            stripe_obj = self.Stripe.query.filter_by(user_id=user_id)
        elif subscription_id != None:
            stripe_obj = self.Stripe.query.filter_by(subscription_id=subscription_id)
        elif customer_id != None:
            stripe_obj = self.Stripe.query.filter_by(customer_id=customer_id)

        if get_all:
            return stripe_obj.all()
        else:
            return stripe_obj.first()

    def stripe_obj_to_dict(self, stripe_obj):
        return {c.key: getattr(stripe_obj, c.key)
                for c in inspect(stripe_obj).mapper.column_attrs}

    def update_stripe_by_dict(self, stripe_id, stripe_obj):
        stripe_row = self.Stripe.query.filter_by(id=stripe_id).first()
        stripe_row.update(**stripe_obj)
        self.db.session.commit()