from flask import Flask, render_template
import os

base_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
frontend_dir = os.path.join(base_dir, 'frontend')
template_dir = os.path.join(frontend_dir, 'templates')
static_dir = os.path.join(frontend_dir, 'static')

app = Flask(__name__, 
            template_folder=template_dir,
            static_url_path='', 
            static_folder=static_dir)

@app.route("/")
def home():
    return render_template('index.ejs')
    
@app.route("/login-page")
def login_page():
    return render_template('login-page.ejs')

@app.route("/billing")
def billing():
    return render_template('billing.ejs')

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.ejs')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')