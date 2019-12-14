# Flask Stripe MySQL Bootstrapped
This template is ready for scaling and is easy to deploy.

![Signup, Login and Stripe Demo!](demo/showcase.gif)

# After Installation

You can at any point login to your MySQL database, containing multiple databases.

Currently, there is one database (UserDB) with one table (user).

1. See login instructions in the installation section
2. Once logged in, you can do `USE UserDB;`
3. Then you can do `DESCRIBE user;`
4. And you can also look at all your users `SELECT * FROM user;`

# Technologies and features

- [x] Python & MySQL Database
- [x] Stripe for secure payments: creating subscriptions and automated billing at the end of each month.
- [x] Bootstrapped, pretty theme with a dashboard (using [Creative](https://startbootstrap.com/themes/creative/) and [SB Admin 2](https://startbootstrap.com/themes/sb-admin-2/))
- [x] Flask as Backend, serving HTML, CSS and JS
- [x] Simplistic REST API with Flask
- [x] Reusing HTML files when loading pages, including scripts, for performance
- [x] Complete signup and login system, user data stored in MySQL database
- [x] Error handling
- [x] Secure against XSS, CSRF attacks (i.e. you cannot send POST requests to the /signup endpoint, because it will be rejected with no CSRF token)
- [x] 7-day Trial Period For Subscribers
- [x] Page-template with an included Terms of Service (TOS) page
- [ ] Docker: Gunicorn+Docker for this web app.
- [ ] Docker: Machine Learning sample model in Gunicorn+Docker container.
- [ ] Docker: Make 2 docker containers interact.
- [ ] Email validation
- [ ] Logging errors in database
- [ ] Feedback button to store feedback in database
- [ ] Account Details (update account, disable account)
- [ ] Settings for app
- [ ] Signup and Login with Facebook / Google
- [ ] Multiprocessing with Gunicorn, for SQLAlchemy and MySQL
- [ ] Automatic in-app notifications — offer annual payment after 1 months use, notify user of credit card expiring soon.
- [ ] Easy pricing strategy provided. Monthly for $xx and annual for $xx, get 2 months free. Extremely transparent pricing strategy, annual being standard and opt-of, with the benefits you lose if you switch to monthly.

## Todo

- Build the app into an actual architecture http://dev.nando.audio/2014/04/01/large_apps_with_sqlalchemy__architecture.html
    - Which layers and what do they do?
    - Unit/integration testing?
    - Logging?
    - Microservices?
- Fix create_subscription_in_db when user is none
- Split some HTML in partial files
- Add ability to have multiple subscriptions
- List all subscriptions
- Move on to upgrading/downgrading monthly and yearly plans
- Add billing information (invoice date, description, amount, was it paid)

# Installation

1. Install Python (3.7 was used for this project)
2. Install the package requirements `pip install -r requirements.txt`
3. Download and install MySQL server and run it
- Windows: See Windows section below
- Mac/Linux: See Mac and Linux section below
4. Configure your connector in `backend/db_access.py`. I configured MySQL to run on port 5001, but the default port is 3306, which you can easily switch the port to in the code.

```python
conn = connect(
    host="localhost",
    port='3306',
    user="root",
    passwd="rootpw"
)
```

## Windows

Download [MySQL server](https://dev.mysql.com/downloads/mysql/) and start it.

**\*\*IMPORTANT**: Make sure to check **"Configure MySQL Server as a Windows Service"** and **"Start the MySQL server at System Startup"**. 

Check the service is configured by pressing windows key or WINDOWS KEY+R and typing `services.msc` and find MySQL (e.g. MySQL80). It should be running, also after you have restarted your computer. Always check back here if something is not running.

### Register Environment Variables

A tip that makes your life easier:

1. Press the windows key and search for 'edit environment variables'
2. In the upper section, double click path. Then click new. Then find your installation folder for mysql, e.g. mine was under `C:\Program Files\MySQL\MySQL Server 8.0\bin`. Add it as your path and click ok.
3. Now you can use mysql, mysqld and mysqladmin commands which will be helpful for debugging.

### Login to the database from Windows

Open MySQL vXX Command Line Prompt (e.g. MySQL 8.0 Command Line Prompt) and enter your password, e.g. `rootpw` is used in this repo.

## Mac and Linux

Use Homebrew to install mysql. Installing homebrew is the first step:

1. Install homebrew: `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`
2. Install mysql `brew install mysql`
3. Check it's installed `mysql -V`
4. Locate your mysql config file. Mine was under `/usr/local/etc/my.cnf`, but check `/etc/my.cnf` or `/etc/mysql/my.cnf` or `~/.my.cnf` if you can't find it.
5. (you can skip this, but I prefer it) Change your default port from 3306 by opening `my.cnf`. Add a new line with `port=5001`
6. Start mysql `brew services start mysql` (starts every time you boot computer)
7. Configure your password `mysqladmin -u root password 'yourpassword'`. This password should be strong if used in production.

You can always restart or stop the service, e.g. if the service is running and you edit your config file, you need to restart the service for it to pick it up:

- `brew services restart mysql`
- `brew services stop mysql`

### Login to MySQL database

Type in `mysqladmin -u root -p` and press enter. It will ask for your password, then you are in.
