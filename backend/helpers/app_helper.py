from flask_login import current_user
from backend.models import Stripe
import time
from datetime import datetime

def is_user_subscription_active(billing_page = True):
    timestamp = time.time()

    sub_active = None
    show_reactivate = None
    sub_cancelled_at = None

    stripe_obj = Stripe.query.filter_by(user_id=current_user.id, subscription_active=True).first()

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