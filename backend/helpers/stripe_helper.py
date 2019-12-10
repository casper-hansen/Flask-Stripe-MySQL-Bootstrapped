from flask import Flask, current_app
import stripe
import json

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