from flask import Flask, render_template
import os

template_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
template_dir = os.path.join(template_dir, 'frontend')
template_dir = os.path.join(template_dir, 'templates')

static_folder='web/static'

app = Flask(__name__, template_folder=template_dir)

@app.route("/")
def hello():
    return render_template('index.ejs')

    
@app.route("/login-page")
def login():
    return render_template('login-page.ejs')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')