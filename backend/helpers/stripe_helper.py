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

def update_subscription_when_paid(data, already_called = False):
    '''
        Method for updating a subscription, when it has been paid.
    '''
    if data['type'] == 'invoice.payment_succeeded':
        # Get data object and subscription id
        data_object = data['data']['object']
        sub_id = data_object['subscription']

        # If the subscription id is null, we can't update the subscription
        if sub_id == None:
            return "subscription_id was null", 402

        stripe_obj = Stripe.query.filter_by(subscription_id=sub_id).first()
        
        if stripe_obj != None:
            # Find the new end of period
            stripe_obj.current_period_end = data_object['lines']['data'][0]['period']['end']

            # Get the payment method to setup the default payment method
            pi = stripe.PaymentIntent.retrieve(data_object['payment_intent'])

            if stripe_obj.payment_method_id == None:
                stripe_obj.payment_method_id = pi['payment_method']

                stripe.Customer.modify(
                    stripe_obj.customer_id,
                    invoice_settings={'default_payment_method': stripe_obj.payment_method_id}
                )

            db.session.commit()
            return "", 200
        else:
            create_subscription_in_db(sub_id)
            if not already_called:
                update_subscription_when_paid(data, True)

            return "subscription_id did not exist, created a new row", 200
    else:
        return "Wrong request type", 400

def create_subscription_in_db(subscription_id):
    '''
        Given a subscription id, create the subscription in database.
        Finds all the relevant information from the stripe subscription object
    '''
    # Get the subscription object and customer_id
    sub = stripe.Subscription.retrieve(subscription_id)
    customer_id = sub['customer']

    # Find the customer in db
    stripe_obj = Stripe.query.filter_by(customer_id=customer_id).first()

    if stripe_obj != None:
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

def is_subscription_id_present_in_user(user_id, sub_id):
    '''
        Provided a user id and subscription id, check if the user has
        the provided subscription id.
        Returns the row in database where the subscription id exists
    '''
    stripe_obj = Stripe.query.filter_by(user_id=user_id).all()

    # If the provided subscription id exists, return the row
    for row in stripe_obj:
        if row.subscription_id == sub_id:
            return row, True
        
    return None, False