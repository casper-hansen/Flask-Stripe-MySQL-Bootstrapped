from flask import Flask, render_template, redirect, request, escape
from flask_login import LoginManager, login_required, login_user, logout_user 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import os

base_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
frontend_dir = os.path.join(base_dir, 'frontend')
template_dir = os.path.join(frontend_dir, 'templates')
static_dir = os.path.join(frontend_dir, 'static')

app = Flask(__name__, 
            template_folder=template_dir,
            static_url_path='', 
            static_folder=static_dir)

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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self):
        return 'id: '.join([id])

db.create_all()

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
    return render_template('login-page.html')

@app.route("/login", methods=["POST"])
def login():
    email = escape(request.form['email'])
    password = escape(request.form['password'])

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

@app.route("/getusers")
def users():
    users = User.query.all()
    print(users)
    return 'Hello'

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')