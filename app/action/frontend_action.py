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

class FrontendAction():
    def __init__(self, db, app, User, Notifications, Stripe):
        self.User = User
        self.Notifications = Notifications
        self.Stripe = Stripe
        self.db = db
        self.app = app

    def is_user_subscription_active(self, billing_page = True):
        timestamp = time.time()

        sub_active = None
        show_reactivate = None
        sub_cancelled_at = None

        stripe_obj = self.Stripe.query.filter_by(user_id=current_user.id, subscription_active=True).first()

        if stripe_obj != None:
            if stripe_obj.subscription_cancelled_at != None and timestamp < stripe_obj.subscription_cancelled_at:
                show_reactivate = True
            sub_active = stripe_obj.subscription_active
            sub_cancelled_at = stripe_obj.subscription_cancelled_at
            
            if billing_page and sub_cancelled_at != None:
                sub_cancelled_at =  datetime.utcfromtimestamp(sub_cancelled_at).strftime('%Y-%m-%d %H:%M:%S')

        if billing_page:
            return sub_active, show_reactivate, sub_cancelled_at
        else:
            return sub_active

    def get_ending(self, num):
        num = int(num)
        date_suffix = ["th", "st", "nd", "rd"]

        if num % 10 in [1, 2, 3] and num not in [11, 12, 13]:
            return date_suffix[num % 10]
        else:
            return date_suffix[0]

    def subscriptions_to_json(self, stripe_subscriptions):
        keys_to_return = ['current_period_end',
                        'subscription_active', 
                        'amount',
                        'subscription_cancelled_at',
                        'subscription_id']
        
        return_arr = []

        for row in stripe_subscriptions:
            new_dict = {}
            for key in keys_to_return:
                if key == 'current_period_end':
                    dt = datetime.utcfromtimestamp(eval('row.' + key))
                    ending = self.get_ending(dt.day)
                    dt_formatted = dt.strftime('%B %d{0}, %Y'.format(ending))
                    new_dict['Renew Date'] = dt_formatted
                elif key == 'subscription_active':
                    value = eval('row.' + key)
                    new_dict['Subscription Active'] = 'YES' if value == True else 'NO'
                elif key == 'amount':
                    new_dict['Price'] = "$" + str(eval('row.' + key)/100)
                elif key == 'subscription_id':
                    new_dict[key] = eval('row.' + key)
                elif key == 'subscription_cancelled_at':
                    timestamp = time.time()
                    value = eval('row.' + key)

                    if value == None:
                        # Show cancel button
                        new_dict['cancel_in_progress'] = None
                    elif timestamp < value:
                        # If current time is before the time when subscription is cancelled
                        # Show reactivate button
                        new_dict['cancel_in_progress'] = True
                    else:
                        # Show no button
                        new_dict['cancel_in_progress'] = False
            return_arr.append(new_dict)

        return return_arr