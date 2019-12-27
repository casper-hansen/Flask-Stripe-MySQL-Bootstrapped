from flask import Flask, current_app
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
import stripe, json, sys, os, traceback, requests
from datetime import timedelta, datetime
from data_access.stripe_db import StripeAccess
from types import SimpleNamespace

db_access = StripeAccess()

class StripeAction():
    def __init__(self, app):
        self.app = app
        self.user_service = 'http://localhost:' + app.config['USER_PORT'] + '/'

        stripe.api_key = app.config['STRIPE_SECRET_KEY']  

    def setup_payment(self, request):
        try:
            # Get the data from AJAX request
            data = request.get_json(force=True)

            # Find the plan id in the config file
            plan = self.app.config['STRIPE_PLAN_' + data['plan']]

            # Get stripe obj from database
            stripe_obj = db_access.get_stripe(user_id=data['user_id'])

            # Get user object from user service
            r = requests.get(self.user_service + 'getuser/' + str(data['user_id']))
            if r.status_code != 200:
                return json.dumps({'message': 'something went wrong'})
                
            user_json = json.loads(r.text)
            user = SimpleNamespace(**user_json)

            customer_id = None
            if stripe_obj != None and stripe_obj.customer_id != None:
                customer_id = stripe_obj.customer_id

            base_url = self.app.config['PROTOCOL'] + '://' + self.app.config['BASE_URL']
            
            # Setup a Stripe session, completed with a webhook
            session = stripe.checkout.Session.create(
                customer_email=user.email,
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
            variables = dict(stripe_public_key=self.app.config['STRIPE_PUBLIC_KEY'],
                            session_id=session.id)

            return json.dumps(variables), 200
        except Exception as ex:
            stacktrace = traceback.format_exc()
            print(stacktrace)
            return json.dumps({'message':'Something went wrong'}), 500

    def cancel_subscription(self, request):
        try:
            data = request.get_json(force=True)
            stripe_id, is_present = self._is_subscription_id_present_in_user(data['user_id'], data['sub_id'])

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
            stripe_update = dict(subscription_cancelled_at=int(timestamp))
            db_access.update_stripe_by_dict(stripe_id, stripe_update)

            variables = dict(message='Success. You unsubscribed and will not be billed anymore. Your subscription will last until ' + subscription_ends)

            return json.dumps(variables), 200
        except Exception as ex:
            stacktrace = traceback.format_exc()
            print(stacktrace)
            return json.dumps({'message':'Something went wrong'}), 500

    def reactivate_subscription(self, request):
        try:
            data = request.get_json(force=True)
            stripe_id, is_present = self._is_subscription_id_present_in_user(data['user_id'], data['sub_id'])

            if not is_present:
                return json.dumps({'message':'User does not have subscription id'}), 401

            session = stripe.Subscription.modify(
                data['sub_id'],
                cancel_at_period_end=False
            )

            stripe_update = dict(subscription_cancelled_at=None)
            db_access.update_stripe_by_dict(stripe_id, stripe_update)

            variables = dict(message='Success. You will automatically be billed every month.')

            return json.dumps(variables), 200
        except Exception as ex:
            stacktrace = traceback.format_exc()
            print(stacktrace)
            return json.dumps({'message':'Something went wrong'}), 500

    def succesful_payment(self, request):
        try:
            # Validate if the request is a valid request received from Stripe
            data = self._validate_stripe_data(request, 'WEBHOOK_SUBSCRIPTION_SUCCESS')

            if data['type'] == 'checkout.session.completed':
                # Find the data object and corresponding user
                data_object = data['data']['object']
                
                # Get user object from user service
                r = requests.get(self.user_service + 'getuser/email/' + data_object['customer_email'])
                if r.status_code != 200:
                    return json.dumps({'message': 'something went wrong'})
                    
                user_json = json.loads(r.text)
                user = SimpleNamespace(**user_json)

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

                    db_access.create_stripe(new_stripe)

            return "", 200
        except IntegrityError:
            return "User already has an active subscription", 400
        except ValueError:
            return "Bad payload", 400
        except stripe.error.SignatureVerificationError:
            return "Bad signature", 400
        except Exception as ex:
            stacktrace = traceback.format_exc()
            print(stacktrace)
            return str(stacktrace), 500

    def invoice_paid(self, request):
        try:
            data = self._validate_stripe_data(request, 'WEBHOOK_NEW_INVOICE')
            return self._update_subscription_when_paid(data)

        except IntegrityError:
            return "Something went wrong", 400
        except ValueError:
            return "Bad payload", 400
        except stripe.error.SignatureVerificationError:
            return "Bad signature", 400
        except Exception as ex:
            stacktrace = traceback.format_exc()
            print(stacktrace)
            return str(stacktrace), 500

    def subscription_ended(self, request):
        try:
            data = self._validate_stripe_data(request, 'WEBHOOK_SUBSCRIPTION_ENDED')

            data_object = data['data']['object']
            if data_object['status'] == 'canceled':
                sub_id = data_object['items']['data'][0]['subscription']
                stripe_obj = db_access.get_stripe(subscription_id=sub_id)

                if stripe_obj != None:
                    stripe_update = dict(subscription_active=False)
                    db_access.update_stripe_by_dict(stripe_obj.id, stripe_update)

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

    def _validate_stripe_data(self, request, webhook_from_config):
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

    def _update_subscription_when_paid(self, data, already_called = False):
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

            stripe_obj = db_access.get_stripe(subscription_id=sub_id)
            
            if stripe_obj != None:
                # Find the new end of period
                stripe_update = dict(current_period_end=data_object['lines']['data'][0]['period']['end'])

                # Get the payment method to setup the default payment method
                pi = stripe.PaymentIntent.retrieve(data_object['payment_intent'])

                if stripe_obj.payment_method_id == None:
                    stripe_obj.payment_method_id = pi['payment_method']

                    stripe.Customer.modify(
                        stripe_obj.customer_id,
                        invoice_settings={'default_payment_method': stripe_obj.payment_method_id}
                    )

                db_access.update_stripe_by_dict(stripe_obj.id, stripe_update)
                return "", 200
            else:
                self._create_subscription_in_db(sub_id)
                if not already_called:
                    self._update_subscription_when_paid(data, True)

                return "subscription_id did not exist, created a new row", 200
        else:
            return "Wrong request type", 400

    def _create_subscription_in_db(self, subscription_id):
        '''
            Given a subscription id, create the subscription in database.
            Finds all the relevant information from the stripe subscription object
        '''
        # Get the subscription object and customer_id
        sub = stripe.Subscription.retrieve(subscription_id)
        customer_id = sub['customer']

        # Find the customer in db
        stripe_obj = db_access.get_stripe(customer_id=customer_id)

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

            db_access.create_stripe(new_stripe)

    def _is_subscription_id_present_in_user(self, user_id, sub_id):
        '''
            Provided a user id and subscription id, check if the user has
            the provided subscription id.
            Returns the row in database where the subscription id exists
        '''
        stripe_obj = db_access.get_stripe(user_id=user_id, get_all=True)

        # If the provided subscription id exists, return the row
        for row in stripe_obj:
            if row.subscription_id == sub_id:
                return row.id, True
            
        return None, False