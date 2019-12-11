from flask import Flask, current_app
import stripe
import json

from backend.stripe import Stripe, db

def validate_stripe_data(request, webhook_from_config):
    '''
        A function for validating webhook content
    '''

    payload = request.data.decode("utf-8")
    received_sig = request.headers.get("Stripe-Signature", None)

    # Verify received data
    with current_app.app_context():
        event = stripe.Webhook.construct_event(
            payload, received_sig, current_app.config[webhook_from_config]
        )

    # JSON to Python Dictionary
    data = json.loads(payload)

    return data

def create_subscription_in_db(subscription_id):
    # Get the subscription object and customer_id
    sub = stripe.Subscription.retrieve(subscription_id)
    customer_id = sub['customer']

    # Find the customer in db
    stripe_obj = Stripe.query.filter_by(customer_id=customer_id).first()

    amount = sub['items']['data'][0]['plan']['amount']
    
    current_period_start = sub['current_period_start']
    current_period_end = sub['current_period_end']

    new_stripe = dict(user_id=stripe_obj.user_id,
                        subscription_id=subscription_id,
                        customer_id=customer_id,
                        subscription_active=True,
                        amount=amount,
                        current_period_start=current_period_start,
                        current_period_end=current_period_end,
                        subscription_cancelled_at=None)

    stripe_row = Stripe(**new_stripe)

    db.session.add(stripe_row)
    db.session.commit()