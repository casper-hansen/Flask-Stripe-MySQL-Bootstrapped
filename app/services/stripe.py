import json
from datetime import datetime
import traceback

from flask import Flask, Blueprint, request
from flask_login import login_required, current_user
import stripe
from sqlalchemy import exc

# Import all the things
from backend import app, db, User, Stripe, Notifications, login_manager, csrf
from helpers.stripe_helper import validate_stripe_data, update_subscription_when_paid, is_subscription_id_present_in_user

# Every route from here will be imported to app.py through the stripe_api Blueprint
stripe_api = Blueprint('stripe_api', __name__)
stripe.api_key = app.config['STRIPE_SECRET_KEY']

@stripe_api.route("/setup_payment", methods=["POST"])
@login_required
def setup_payment():
    '''
        Endpoint for setting up a subscription with a redirect to Stripe.
        
        Upon click the "Choose this plan", the plan clicked on is sent
        in a post request to this endpoint. We create a stripe checkout session
        where the user can provide payment information for creating the
        subscription clicked on.

        If succesful, the STRIPE_PUBLIC_KEY and session_id is returned.
        This information is used by the Stripe javascript library to redirect
        to Stripe's site for payment.

        Parameters
        ----------
        request : JSON data
            Has to contain the name of the plan.

        Returns
        -------
        stripe_public_key : string (JSON)
            The public key from the config.py file
        
        session_id : string (JSON)
            The session id created from stripe.checkout.Session.create()
    '''
    try:
        # Get the data from AJAX request
        data = request.get_json(force=True)

        # Find the plan id in the config file
        plan = app.config['STRIPE_PLAN_' + data['plan']]

        stripe_obj = Stripe.query.filter_by(user_id=current_user.id).first()
        customer_id = None
        if stripe_obj != None and stripe_obj.customer_id != None:
            customer_id = stripe_obj.customer_id

        base_url = app.config['PROTOCOL'] + '://' + app.config['BASE_URL']

        # Setup a Stripe session, completed with a webhook
        session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            customer=customer_id,
            payment_method_types=['card'],
            subscription_data={
                'items': [{
                    'plan': plan,
                }],
            },
            success_url=base_url + '/billing',
            cancel_url=base_url +'/dashboard',
        )

        # Used for redirect
        variables = dict(stripe_public_key=app.config['STRIPE_PUBLIC_KEY'],
                         session_id=session.id)

        return json.dumps(variables), 200
    except Exception as ex:
        stacktrace = traceback.format_exc()
        print(stacktrace)
        return json.dumps({'message':'Something went wrong'}), 500
    
@stripe_api.route("/cancel_subscription", methods=["PUT"])
@login_required
def cancel_subscription():
    '''
        Endpoint for cancelling an active subscription.

        Parameters
        ----------
        request : JSON data
            Has to contain the subscription_id for cancellation.

        Returns
        -------
        message : string (JSON)
            Renders a success string with information about when the subscription
            finally ends (at the end of the period).
    '''
    try:
        data = request.get_json(force=True)
        stripe_obj, is_present = is_subscription_id_present_in_user(current_user.id, data['sub_id'])

        if not is_present:
            return json.dumps({'message':'User does not have subscription id'}), 401

        # Cancel at period end means that the subscription is still active,
        # and the user still has access to the service for the currently paid period.
        session = stripe.Subscription.modify(
            data['sub_id'],
            cancel_at_period_end=True
        )

        timestamp = session['cancel_at']
        subscription_ends = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        stripe_obj.subscription_cancelled_at = int(timestamp)
        db.session.commit()

        variables = dict(message='Success. You unsubscribed and will not be billed anymore. Your subscription will last until ' + subscription_ends)

        return json.dumps(variables), 200
    except Exception as ex:
        stacktrace = traceback.format_exc()
        print(stacktrace)
        return json.dumps({'message':'Something went wrong'}), 500

@stripe_api.route("/reactivate_subscription", methods=["PUT"])
@login_required
def reactivate_subscription():
    '''
        Endpoint for reactivating a cancelled subscription.

        Parameters
        ----------
        request : JSON data
            Has to contain the subscription_id for cancellation.

        Returns
        -------
        message : string (JSON)
            Renders a success string.
    '''
    try:
        data = request.get_json(force=True)
        stripe_obj, is_present = is_subscription_id_present_in_user(current_user.id, data['sub_id'])

        if not is_present:
            return json.dumps({'message':'User does not have subscription id'}), 401

        session = stripe.Subscription.modify(
            data['sub_id'],
            cancel_at_period_end=False
        )

        stripe_obj.subscription_cancelled_at = None
        db.session.commit()

        variables = dict(message='Success. You will automatically be billed every month.')

        return json.dumps(variables), 200
    except Exception as ex:
        stacktrace = traceback.format_exc()
        print(stacktrace)
        return json.dumps({'message':'Something went wrong'}), 500

@stripe_api.route("/webhook_pay_success", methods=["POST"])
@csrf.exempt
def succesful_payment():
    '''
        Endpoint for receving the checkout.session.complete webhook request from Stripe. 
        

        Parameters
        ----------
        request : JSON data
            This is a payload from Stripe. Contains Stripe's Checkout Session object.

        Returns
        -------
        message : string
            Empty string if the request went well. Contains debugging information
            if the request went bad.
        status : int
            HTTP status code.
    '''
    try:
        # Validate if the request is a valid request received from Stripe
        data = validate_stripe_data(request, 'WEBHOOK_SUBSCRIPTION_SUCCESS')

        if data['type'] == 'checkout.session.completed':
            # Find the data object and corresponding user
            data_object = data['data']['object']
            user = User.query.filter_by(email=data_object['customer_email']).first()

            if user != None:
                # Get the stripe subscription
                sub = stripe.Subscription.retrieve(data_object['subscription'])

                # Find and update the subscription data
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

                stripe_row = Stripe(**new_stripe)

                db.session.add(stripe_row)
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

@stripe_api.route("/webhook_invoice_paid", methods=["POST"])
@csrf.exempt
def invoice_paid():
    '''
        Endpoint for receving the invoice.payment_succeeded from Stripe. 
        When the customer pays his subscription for another month,
        we need to update when his current_period_end in the db.

        (Webhook is also received the first time the customer pays. In
         any case, this will not be a problem. It's handled correctly.)

        Parameters
        ----------
        request : JSON data
            This is a payload from Stripe.

        Returns
        -------
        message : string
            Empty string if the request went well. Contains debugging information
            if the request went bad.
        status : int
            HTTP status code.
    '''

    try:
        data = validate_stripe_data(request, 'WEBHOOK_NEW_INVOICE')
        return update_subscription_when_paid(data)

    except exc.IntegrityError:
        return "Something went wrong", 400
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
        Endpoint for receving the customer.subscription.deleted from Stripe. 
        This webhook is received if the user cancelled his subscription
        at an earlier time, and the current_period_end in the database
        is less than current time.

        When a subscription is cancelled, the subscription lasts for the
        period paid. When the period is over, this webhook is sent from
        Stripe.

        Removes all access to the services provided for paid subscriptions.

        Parameters
        ----------
        request : JSON data
            This is a payload from Stripe.

        Returns
        -------
        message : string
            Empty string if the request went well. Contains debugging information
            if the request went bad.
        status : int
            HTTP status code.
    '''
    
    try:
        data = validate_stripe_data(request, 'WEBHOOK_SUBSCRIPTION_ENDED')

        data_object = data['data']['object']
        if data_object['status'] == 'canceled':
            sub_id = data_object['items']['data'][0]['subscription']
            stripe_obj = Stripe.query.filter_by(subscription_id=sub_id).first()

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