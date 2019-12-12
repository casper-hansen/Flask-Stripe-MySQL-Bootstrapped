from flask_login import current_user
from backend.models import Stripe
import time
from datetime import datetime
import json

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

def subscriptions_to_json(stripe_subscriptions):
    keys_to_return = ['current_period_end',
                      'subscription_active', 
                      'amount',
                      'subscription_id']
    
    return_arr = []
    for row in stripe_subscriptions:
        new_dict = {}
        for key in keys_to_return:
            if key == 'current_period_end':
                new_dict['Subscription Ends'] = datetime.utcfromtimestamp(eval('row.' + key)).strftime('%Y-%m-%d %H:%M:%S')
            elif key == 'subscription_active':
                value = eval('row.' + key)
                new_dict['Subscription Active'] = 'YES' if value == True else 'NO'
            elif key == 'amount':
                new_dict['Paid'] = "$" + str(eval('row.' + key)/100)
            elif key == 'subscription_id':
                new_dict[key] = eval('row.' + key)
        return_arr.append(new_dict)

    return return_arr
    #return json.dumps(return_arr)