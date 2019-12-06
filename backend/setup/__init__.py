import os
from sqlalchemy import create_engine
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
import jinja2

base_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..'))
frontend_dir = os.path.join(base_dir, 'frontend')
template_dir = os.path.join(frontend_dir, 'templates')
static_dir = os.path.join(frontend_dir, 'static')
base_template_dir = os.path.join(template_dir, 'base_templates')

app = Flask(__name__, 
            root_path=base_dir,
            static_url_path='', 
            static_folder=static_dir)

my_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader([template_dir, 
                                 base_template_dir]),
    ])
app.jinja_loader = my_loader

app.config.from_pyfile('env_variables.py')

CONN_STR = "mysql+mysqlconnector://{0}:{1}@{2}:{3}" \
    .format(app.config['MYSQL_USER'], app.config['MYSQL_PASSWORD'], app.config['MYSQL_HOST'], app.config['MYSQL_PORT'])

CONN_STR_W_DB = CONN_STR + '/' + app.config['MYSQL_DB_NAME']

app.config['CONN_STR'] = CONN_STR
app.config['CONN_STR_W_DB'] = CONN_STR_W_DB

mysql_engine = create_engine(app.config['CONN_STR'])
mysql_engine.execute("CREATE DATABASE IF NOT EXISTS {0}".format(app.config['MYSQL_DB_NAME']))

app.config['SQLALCHEMY_DATABASE_URI'] = app.config['CONN_STR_W_DB']

db = SQLAlchemy(app)

# Import user after setup (important)
from backend.setup.models import User

# Within our app context, create all missing tables
db.create_all()
login_manager = LoginManager(app)
login_manager.session_protection = 'basic'
csrf = CSRFProtect(app)

