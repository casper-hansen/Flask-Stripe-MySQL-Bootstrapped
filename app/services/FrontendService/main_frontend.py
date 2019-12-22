import sys
import json
import os
import stripe
from datetime import timedelta, datetime
from flask import Flask, render_template, redirect, request, escape, jsonify, flash, current_app
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_wtf import CSRFProtect

base_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..'))
sys.path.append(base_dir)

# Import all the things
from backend import app, db, User, Notifications, Stripe
from action.frontend_action import FrontendAction
from call_notifications_service import notification_api
from call_user_service import user_api

csrf = CSRFProtect(app)
app.register_blueprint(notification_api)
app.register_blueprint(user_api)

action = FrontendAction(db, app, User, Notifications, Stripe)

@app.route("/")
def home():
    variables = dict(is_authenticated=current_user.is_authenticated)
    return render_template('index.html', **variables)

@app.route("/login_page")
def login_page():
    if current_user.is_authenticated:
        return redirect('/dashboard', code=302)
    return render_template('login_page.html')

@app.route("/dashboard")
@login_required
def dashboard():
    trial_period = timedelta(days=app.config['TRIAL_LENGTH_DAYS'])

    sub_active = action.is_user_subscription_active(False)

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
    sub_active, show_reactivate, sub_cancelled_at = action.is_user_subscription_active()
    stripe_obj = Stripe.query.filter_by(user_id=current_user.id).all()

    sub_dict = action.subscriptions_to_json(stripe_obj)

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
    app.run(host='0.0.0.0', port=5000)