import json
import os
from datetime import timedelta

from flask import Flask, Blueprint, render_template, redirect, request, escape, jsonify, flash, current_app
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
import stripe

from backend.setup import app, db, User, login_manager, csrf

stripe_api = Blueprint('stripe_api', __name__)

@stripe_api.route("/setup_payment", methods=["POST"])
@login_required
def setup_payment():
    try:
        data = request.get_json(force=True)
        plan = current_app.config['STRIPE_PLAN_' + data['plan']]

        session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            payment_method_types=['card'],
            subscription_data={
                'items': [{
                    'plan': plan,
                }],
            },
            success_url='http://localhost:5000/billing',
            cancel_url='http://localhost:5000/dashboard',
        )

        variables = dict(stripe_public_key=current_app.config['STRIPE_PUBLIC_KEY'],
                         session_id=session.id)

        return json.dumps(variables), 200
    except Exception as ex:
        return json.dumps({'message':'Something went wrong'}), 401
    
    
@stripe_api.route("/webhook_pay_success", methods=["POST"])
@csrf.exempt
def succesful_payment():
    payload = request.data.decode("utf-8")
    received_sig = request.headers.get("Stripe-Signature", None)

    try:
        with current_app.app_context():
            event = stripe.Webhook.construct_event(
                payload, received_sig, current_app.config['ENDPOINT_SECRET']
            )
    except ValueError:
        print("Error while decoding event!")
        return "Bad payload", 400
    except stripe.error.SignatureVerificationError:
        print("Invalid signature!")
        return "Bad signature", 400

    data = json.loads(payload)
    if data['type'] == 'checkout.session.completed':
        data_object = data['data']['object']
        user = User.query.filter_by(email=data_object['customer_email']).first()

        if user != None:
            user.subscription_active = True
            user.subscription_id = data_object['subscription']
            user.customer_id = data_object['customer']
            db.session.commit()

    return "", 200
