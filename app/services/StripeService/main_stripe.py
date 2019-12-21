import sys
import os
import stripe
from flask import request
from flask_login import login_required, current_user

base_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..'))
sys.path.append(base_dir)

# Import all the things
from backend import app, db, User, Stripe, Notifications, login_manager, csrf
from action.stripe_action import StripeAction

action = StripeAction(Stripe, db, app, User)

@app.route("/setup_payment", methods=["POST"])
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

        Returns (JSON)
        -------
        {
            stripe_public_key : string
                The public key from the config.py file
            
            session_id : string
                The session id created from stripe.checkout.Session.create()
        }
    '''
    return action.setup_payment(request)

@app.route("/cancel_subscription", methods=["PUT"])
@login_required
def cancel_subscription():
    '''
        Endpoint for cancelling an active subscription.

        Parameters
        ----------
        request : JSON data
            Has to contain the subscription_id for cancellation.

        Returns (JSON)
        -------
        {
            message : string 
                Renders a success string with information about when the subscription
                finally ends (at the end of the period).
        }
        
    '''
    return action.cancel_subscription(request)

@app.route("/reactivate_subscription", methods=["PUT"])
@login_required
def reactivate_subscription():
    '''
        Endpoint for reactivating a cancelled subscription.

        Parameters
        ----------
        request : JSON data
            Has to contain the subscription_id for cancellation.

        Returns (JSON)
        -------
        {
            message : string
                Renders a success string.
        }
    '''
    return action.reactivate_subscription(request)

@app.route("/webhook_pay_success", methods=["POST"])
@csrf.exempt
def succesful_payment():
    '''
        Endpoint for receving the checkout.session.complete webhook request from Stripe. 


        Parameters
        ----------
        request : JSON data
            This is a payload from Stripe. Contains Stripe's Checkout Session object.

        Returns (JSON)
        -------
        {
            message : string
                Empty string if the request went well. Contains debugging information
                if the request went bad.
            status : int
                HTTP status code.
        }
    '''
    return action.succesful_payment(request)

@app.route("/webhook_invoice_paid", methods=["POST"])
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

        Returns (JSON)
        -------
        message : string
            Empty string if the request went well. Contains debugging information
            if the request went bad.
        status : int
            HTTP status code.
    '''
    return action.invoice_paid(request)

@app.route("/webhook_subscription_ended", methods=["POST"])
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

        Returns (JSON)
        -------
        message : string
            Empty string if the request went well. Contains debugging information
            if the request went bad.
        status : int
            HTTP status code.
    '''
    return action.subscription_ended(request)

if __name__ == '__main__':
    app.run(host='0.0.0.0')