import json
import os
import time
from datetime import timedelta, datetime

from werkzeug.exceptions import NotFound
from flask import Flask, render_template, redirect, request, escape, jsonify, flash, current_app
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc, desc
import stripe

# Upon this import, backend/setup/__init__.py is run
from backend.services.stripe import app, db, User, Stripe, login_manager, csrf, stripe_api
from backend.helpers.app_helper import is_user_subscription_active, subscriptions_to_json
from backend.models.notifications import Notifications

# Import all routes from stripe.py
app.register_blueprint(stripe_api)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # If you want all HTTP converted to HTTPS
    # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    return response

@app.route("/")
def home():
    variables = dict(is_authenticated=current_user.is_authenticated)
    return render_template('index.html', **variables)

@app.route("/signup", methods=["POST"])
def signup():
    try:
        # Get data from AJAX request
        data = request.get_json(force=True)
        email = data['email']
        password = data['password']

        # Hash the password (store only the hash)
        pw_hash = generate_password_hash(password, 10)

        # Save user in database
        new_user = User(email=email, password_hash=pw_hash)

        # Take the row spot
        db.session.add(new_user)
        db.session.flush()

        # Make notification
        new_notification = Notifications(user_id=new_user.id,
                                        color = 'success',
                                        icon = 'check-circle',
                                        message_preview = 'You are signed up! Thanks for joining this service.',
                                        message = 'You have successfully signed up!')
        db.session.add(new_notification)

        # Commit changes
        db.session.commit()

        return json.dumps({'message':'/login_page'}), 200
    except exc.IntegrityError as ex:
        db.session.rollback()
        return json.dumps({'message':'Email already in use, tried logging in?'}), 403
    except Exception as ex:
        return json.dumps({'message':'Something went wrong'}), 401
    
@app.route("/login_page")
def login_page():
    if current_user.is_authenticated:
        return redirect('/dashboard', code=302)
    return render_template('login_page.html')

@app.route("/login", methods=["POST"])
def login():
    try:
        # Get data from AJAX request
        data = request.get_json(force=True)
        email = data['email']
        password = data['password']

        # Find user
        user = User.query.filter_by(email=email).first()

        # If user exists, check if email and password matches
        if user != None:
            check_pw = check_password_hash(user.password_hash, password)
            if user.email == email and check_pw:
                login_user(user, remember=True)
                return json.dumps({'message':'/dashboard'}), 200
            else:
                return json.dumps({'message':'User data incorrect'}), 401
        else:
            return json.dumps({'message':'Email not registered'}), 401
    except Exception as ex:
        return json.dumps({'message':'Unknown error, we apologize'}), 500

@app.route("/dashboard")
@login_required
def dashboard():
    trial_period = timedelta(days=app.config['TRIAL_LENGTH_DAYS'])

    sub_active = is_user_subscription_active(False)

    #notifications = [['success', 'donate', 'December 7, 2019', '$290.29 has been deposited into your account!'],
    #                 ['warning', 'exclamation-triangle', 'December 2, 2019', "Spending Alert: We've noticed unusually high spending for your account."]]

    notifications = Notifications.query.filter_by(user_id=current_user.id, isRead=False).order_by(Notifications.created_date.desc()).all()
    notifactions_for_display = notifications[0:5]

    variables = dict(email=current_user.email,
                     expire_date=current_user.created_date + trial_period,
                     user_is_paying=sub_active,
                     notifications=notifactions_for_display,
                     n_messages=len(notifications))
    
    return render_template('dashboard.html', **variables)

@app.route("/billing")
@login_required
def billing():
    sub_active, show_reactivate, sub_cancelled_at = is_user_subscription_active()
    stripe_obj = Stripe.query.filter_by(user_id=current_user.id).all()

    sub_dict = subscriptions_to_json(stripe_obj)

    notifications = Notifications.query.filter_by(user_id=current_user.id, isRead=False).order_by(Notifications.created_date.desc()).all()
    notifactions_for_display = notifications[0:5]
    
    variables = dict(subscription_active=sub_active,
                     email=current_user.email,
                     show_reactivate=show_reactivate,
                     subscription_cancelled_at=sub_cancelled_at,
                     subscription_data=sub_dict,
                     notifications=notifactions_for_display,
                     n_messages=len(notifications))
    
    return render_template('billing.html', **variables)

@app.route("/notifications")
@login_required
def notifications_center():
    notifications = Notifications.query.filter_by(user_id=current_user.id).order_by(Notifications.created_date.desc()).all()
    unread = Notifications.query.filter_by(user_id=current_user.id, isRead=False).order_by(Notifications.created_date.desc()).all()
    notifactions_for_display = unread[0:5]

    variables = dict(email=current_user.email,
                     notifications=notifactions_for_display,
                     all_notifications=notifications,
                     n_messages=len(unread))

    return render_template('notifications.html', **variables)

@app.route("/notification_read", methods=["PUT"])
def notification_read():
    try:
        data = request.get_json(force=True)
        noti_id = data['noti_id']

        notifications = Notifications.query.filter_by(id=noti_id).first()
        notifications.isRead = True

        db.session.commit()

        return json.dumps({'message':''}), 200
    except Exception as ex:
        return json.dumps({'message':'Unknown error, we apologize'}), 500

@app.route("/tos")
def terms_of_service():
    variables = dict(is_authenticated=current_user.is_authenticated)
    return render_template('terms_of_service.html', **variables)

@app.route("/logout")
def logout():
    if current_user.is_authenticated == True:
        current_user.is_authenticated = False
        logout_user()
    return redirect('/', code=302)
    
@app.errorhandler(401)
def not_logged_in(e):
    variables = dict(message='Please login first')
    
    return render_template('login_page.html', **variables)

@app.errorhandler(404)
def not_found(e):
    variables = dict(is_authenticated=current_user.is_authenticated,
                     message = '404 Page Not Found',
                     stacktrace = str(e))
    
    return render_template('error.html', **variables)

if __name__ == '__main__':
    app.run(host='0.0.0.0')