import os
from sqlalchemy import create_engine
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Making the Flask app
app = Flask(__name__)

# Load the config file
app.config.from_pyfile('config.py')

# Make database connection strings
CONN_STR = "mysql+mysqlconnector://{0}:{1}@{2}:{3}" \
    .format(app.config['MYSQL_USER'], app.config['MYSQL_PASSWORD'], app.config['MYSQL_HOST'], app.config['MYSQL_PORT'])
CONN_STR_W_DB = CONN_STR + '/' + app.config['MYSQL_DB_NAME']
app.config['CONN_STR'] = CONN_STR
app.config['CONN_STR_W_DB'] = CONN_STR_W_DB

# Create the database if it does not exist yet
mysql_engine = create_engine(app.config['CONN_STR'])
mysql_engine.execute("CREATE DATABASE IF NOT EXISTS {0}".format(app.config['MYSQL_DB_NAME']))

# Setup the final connection string for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['CONN_STR_W_DB']
db = SQLAlchemy(app)

# Import stripe after setup (important)
from stripe_obj import Stripe

# Within our app context, create all missing tables
db.create_all()

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # If you want all HTTP converted to HTTPS
    # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    return response

print('>>>App is setup')