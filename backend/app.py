from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_required, login_user, logout_user 
import os

base_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
frontend_dir = os.path.join(base_dir, 'frontend')
template_dir = os.path.join(frontend_dir, 'templates')
static_dir = os.path.join(frontend_dir, 'static')

app = Flask(__name__, 
            template_folder=template_dir,
            static_url_path='', 
            static_folder=static_dir)

login_manager = LoginManager()
login_manager.init_app(app)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/signup", methods=["POST"])
def signup():
    email = request.form['email']
    password = request.form['password']

    return redirect('/login-page', code=302)
    
@app.route("/login-page")
def login_page():
    return render_template('login-page.html')

@app.route("/login", methods=["POST"])
def login():
    email = request.form['email']
    password = request.form['password']

    return redirect('/dashboard', code=302)

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

@app.route("/billing")
def billing():
    variables = dict(subscription_active=True)
    return render_template('billing.html', **variables)

@app.route("/logout")
def logout():
    return redirect('/', code=302)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')