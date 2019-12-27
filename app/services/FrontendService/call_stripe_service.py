from flask import Flask, Blueprint, request
from flask_login import current_user, login_required
from models.stripe import Stripe, db
import json, requests

stripe_api = Blueprint('stripe_api', __name__)

@stripe_api.route("/setup_payment", methods=["POST"])
@login_required
def setup_payment():
    data = request.get_json(force=True)
    data['user_id'] = current_user.id

    r = requests.post('http://127.0.0.1:5004/setup_payment', json=data)

    return r.text, r.status_code

@stripe_api.route("/cancel_subscription", methods=["PUT"])
@login_required
def cancel_subscription():
    data = request.get_json(force=True)
    data['user_id'] = current_user.id

    r = requests.put('http://127.0.0.1:5004/cancel_subscription', json=data)

    return r.text, r.status_code

@stripe_api.route("/reactivate_subscription", methods=["PUT"])
@login_required
def reactivate_subscription():
    data = request.get_json(force=True)
    data['user_id'] = current_user.id

    r = requests.put('http://127.0.0.1:5004/reactivate_subscription', json=data)

    return r.text, r.status_code
