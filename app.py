import json

from flask import Flask, render_template, redirect, request, escape, jsonify, flash, current_app
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

from backend.setup import app, db, User
with app.app_context():
    db.create_all()
    login_manager = LoginManager()
    login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route("/")
def home():
    variables = dict(is_authenticated=current_user.is_authenticated)
    return render_template('index.html', **variables)

@app.route("/signup", methods=["POST"])
def signup():
    email = escape(request.form['email'])
    password = escape(request.form['password'])
    
    pw_hash = generate_password_hash(password, 10)

    new_user = User(email=email, password_hash=pw_hash)
    db.session.add(new_user)
    db.session.commit()
    db.engine.dispose()

    return redirect('/login-page', code=302)
    
@app.route("/login-page")
def login_page():
    if current_user.is_authenticated:
        return redirect('/dashboard', code=302)
    return render_template('login-page.html')

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    email = data[0]['value']
    password = data[1]['value']
    user = User.query.filter_by(email=email).first()
    db.engine.dispose()

    if user != None:
        check_pw = check_password_hash(user.password_hash, password)

        if user.email == email and check_pw:
            login_user(user, remember=True)
            return json.dumps({'message':'/dashboard'}), 200
    else:
        return json.dumps({'message':'User data incorrect'}), 401

@app.route("/dashboard")
@login_required
def dashboard():
    variables = dict(email=current_user.email)
    return render_template('dashboard.html', **variables)

@app.route("/billing")
@login_required
def billing():
    variables = dict(subscription_active=current_user.is_subscribed)
    return render_template('billing.html', **variables)

@app.route("/logout")
def logout():
    current_user.is_authenticated = False
    logout_user()
    return redirect('/', code=302)

@app.route("/test")
def users():
    user = User.query.all()
    all_users = ''
    for u in user:
        all_users += u.email + ' / ' + u.password_hash + '<br>'
    return all_users

@app.errorhandler(401)
def not_logged_in(e):
    variables = dict(message='Please login first')
    
    return render_template('login-page.html', **variables)

@app.errorhandler(404)
def not_logged_in(e):
    variables = dict(is_authenticated=current_user.is_authenticated,
                     message = '404 Page Not Found',
                     stacktrace = str(e))
    
    return render_template('error.html', **variables)

if __name__ == '__main__':
    app.run(host='0.0.0.0')