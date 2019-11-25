from flask import Flask, render_template, redirect, request, escape, jsonify, flash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import json
import os

base_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
frontend_dir = os.path.join(base_dir, 'frontend')
template_dir = os.path.join(frontend_dir, 'templates')
static_dir = os.path.join(frontend_dir, 'static')

app = Flask(__name__, 
            template_folder=template_dir,
            static_url_path='', 
            static_folder=static_dir)
app.secret_key = 'super secret string'

host="localhost"
port='5001'
user="root"
password="rootpw"
db_name = "UserDB"

conn_str = "mysql+mysqlconnector://{0}:{1}@{2}:{3}" \
            .format(user, password, host, port)

mysql_engine = create_engine(conn_str)
mysql_engine.execute("CREATE DATABASE IF NOT EXISTS {0}".format(db_name))

conn_str = "mysql+mysqlconnector://{0}:{1}@{2}:{3}/{4}" \
           .format(user, password, host, port, db_name)

app.config['SQLALCHEMY_DATABASE_URI'] = conn_str
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_authenticated = True

    def __repr__(self):
        return 'id: '.join([id])

db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/signup", methods=["POST"])
def signup():
    email = escape(request.form['email'])
    password = escape(request.form['password'])
    
    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

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
    if user != None and user.email == email and user.password == password:
        login_user(user, remember=True)
        return json.dumps({'message':'/dashboard'}), 200
    else:
        return json.dumps({'message':'User data incorrect'}), 401

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route("/billing")
@login_required
def billing():
    variables = dict(subscription_active=True)
    return render_template('billing.html', **variables)

@app.route("/logout")
def logout():
    logout_user()
    return redirect('/', code=302)

@app.route("/test")
def users():
    user = User.query.filter_by(email='q@q.q').first()
    return user.email + '/' + user.password

@app.errorhandler(404)
def not_logged_in(e):
    return redirect('/login-page', code=302)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')