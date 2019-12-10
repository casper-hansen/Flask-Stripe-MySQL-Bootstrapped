import json
from datetime import datetime
import traceback

from flask import Flask, Blueprint, request
from flask_login import login_required, current_user
import stripe
from sqlalchemy import exc

from backend.setup import app, db, User, Stripe, login_manager, csrf
from backend.helpers.stripe_helper import validate_stripe_data

# Every route from here will be imported to app.py through the stripe_api Blueprint
stripe_api = Blueprint('stripe_api', __name__)
stripe.api_key = app.config['STRIPE_SECRET_KEY']

@stripe_api.route("/setup_payment", methods=["POST"])
@login_required
def setup_payment():
    try:
        # Get the data from AJAX request
        data = request.get_json(force=True)
        plan = app.config['STRIPE_PLAN_' + data['plan']]

        # Setup a Stripe session, completed with a webhook
        session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            payment_method_types=['card'],
            subscription_data={
                'items': [{
                    'plan': plan,
                }],
            },
            success_url=app.config['BASE_URL'] + '/billing',
            cancel_url=app.config['BASE_URL'] +'/dashboard',
        )

        variables = dict(stripe_public_key=app.config['STRIPE_PUBLIC_KEY'],
                         session_id=session.id)

        return json.dumps(variables), 200
    except Exception as ex:
        stacktrace = traceback.format_exc()
        print(stacktrace)
        return json.dumps({'message':'Something went wrong'}), 401
    
@stripe_api.route("/webhook_pay_success", methods=["POST"])
@csrf.exempt
def succesful_payment():
    '''
        A function for grabbing correct data and storing it in MySQL db,
        when a user successfully pays on Stripe.
    '''
    try:
        data = validate_stripe_data(request, 'WEBHOOK_SUBSCRIPTION_SUCCESS')

        if data['type'] == 'checkout.session.completed':
            data_object = data['data']['object']
            user = User.query.filter_by(email=data_object['customer_email']).first()

            if user != None:
                sub = stripe.Subscription.retrieve(data_object['subscription'])

                subscription_id = data_object['subscription']
                customer_id = data_object['customer']
                amount = data_object['display_items'][0]['amount']
                
                current_period_start = sub['current_period_start']
                current_period_end = sub['current_period_end']

                new_stripe = dict(user_id=user.id,
                                  subscription_id=subscription_id,
                                  customer_id=customer_id,
                                  subscription_active=True,
                                  amount=amount,
                                  current_period_start=current_period_start,
                                  current_period_end=current_period_end,
                                  subscription_cancelled_at=None)
                
                stripe_obj = Stripe.query.filter_by(user_id=user.id).first()
                if stripe_obj == None:
                    stripe_row = Stripe(**new_stripe)
                    db.session.add(stripe_row)
                else:
                    stripe_obj.update(**new_stripe)
                
                db.session.commit()

        return "", 200
    except exc.IntegrityError:
        return "User already has an active subscription", 400
    except ValueError:
        return "Bad payload", 400
    except stripe.error.SignatureVerificationError:
        return "Bad signature", 400
    except Exception as ex:
        stacktrace = traceback.format_exc()
        print(stacktrace)
        return str(stacktrace), 500

@stripe_api.route("/cancel_subscription", methods=["PUT"])
@login_required
def cancel_subscription():
    try:
        stripe_obj = Stripe.query.filter_by(user_id=current_user.id).first()

        session = stripe.Subscription.modify(
            stripe_obj.subscription_id,
            cancel_at_period_end=True
        )

        timestamp = session['cancel_at']
        subscription_ends = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        stripe_obj.subscription_cancelled_at = int(timestamp)
        db.session.commit()

        variables = dict(message='Success. You unsubscribed and will not be billed anymore. Your subscription will last until' + subscription_ends)

        return json.dumps(variables), 200
    except Exception as ex:
        stacktrace = traceback.format_exc()
        print(stacktrace)
        return json.dumps({'message':'Something went wrong'}), 401

@stripe_api.route("/reactivate_subscription", methods=["PUT"])
@login_required
def reactivate_subscription():
    try:
        stripe_obj = Stripe.query.filter_by(user_id=current_user.id).first()

        session = stripe.Subscription.modify(
            stripe_obj.subscription_id,
            cancel_at_period_end=False
        )

        stripe_obj.subscription_cancelled_at = None
        db.session.commit()

        variables = dict(message='Success. You will automatically be billed every month.')

        return json.dumps(variables), 200
    except Exception as ex:
        stacktrace = traceback.format_exc()
        print(stacktrace)
        return json.dumps({'message':'Something went wrong'}), 401
    
@stripe_api.route("/webhook_invoice_paid", methods=["POST"])
@csrf.exempt
def invoice_paid():
    '''
        When the customer pays his subscription for another month,
        we need to update when his current_period_end in the db
    '''

    try:
        data = validate_stripe_data(request, 'WEBHOOK_NEW_INVOICE')

        if data['type'] == 'invoice.payment_succeeded':
            data_object = data['data']['object']
            stripe_obj = Stripe.query.filter_by(customer_id=data_object['customer']).first()
            
            if stripe_obj != None:
                stripe_obj.current_period_end = data_object['period_end']
                db.session.commit()
                return "", 200
            else:
                return "stripe_obj is null", 202
        else:
            return "Wrong request type", 400
    except ValueError:
        return "Bad payload", 400
    except stripe.error.SignatureVerificationError:
        return "Bad signature", 400
    except Exception as ex:
        stacktrace = traceback.format_exc()
        print(stacktrace)
        return str(stacktrace), 500

@stripe_api.route("/webhook_subscription_ended", methods=["POST"])
@csrf.exempt
def subscription_ended():
    '''
        If the customer has cancelled the subscription, this webhook
        will be sent at the end of the current period, to cancel
        any access to the service.
    '''
    
    try:
        data = validate_stripe_data(request, 'WEBHOOK_SUBSCRIPTION_ENDED')

        data_object = data['data']['object']
        if data_object['status'] == 'canceled':
            stripe_obj = Stripe.query.filter_by(customer_id=data_object['customer']).first()

            if stripe_obj != None:
                stripe_obj.subscription_active = False
                db.session.commit()

                return "", 200
            else:
                return "stripe_obj is null", 500
    except ValueError:
        return "Bad payload", 400
    except stripe.error.SignatureVerificationError:
        return "Bad signature", 400
    except Exception as ex:
        stacktrace = traceback.format_exc()
        print(stacktrace)
        return str(stacktrace), 500