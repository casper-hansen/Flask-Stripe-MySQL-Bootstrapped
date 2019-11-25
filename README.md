# docker-flask-startup-template
Serving a pretty bootstrapped frontend with login page and payment integration. Using docker, flask and stripe in Python.

# Installation

1. Install Python (3.7 was used for this project)
2. Install the package requirements `pip install requirements.txt`
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

**\*\*IMPORTANT** to check the "Configure MySQL Server as a Windows Service" and "Start the MySQL server at System Startup". Check the service is configured by pressing windows key or WINDOWS KEY+R and typing `services.msc` and find MySQL (e.g. MySQL80). It should be running, also after you have restarted your computer. Always check back here if something is not running.

A tip that makes your life easier:

1. Press the windows key and search for 'edit environment variables'
2. In the upper section, double click path. Then click new. Then find your installation folder for mysql, e.g. mine was under `C:\Program Files\MySQL\MySQL Server 8.0\bin`. Add it as your path and click ok.
3. Now you can use mysql, mysqld and mysqladmin commands which will be helpful for debugging.

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

# Technologies and features

- [x] Python & MySQL Database
- [x] Simplistic REST API with Flask
- [x] Flask as Backend, serving HTML, CSS and JS
- [x] Reusing HTML files when loading pages, including scripts, for performance
- [x] Bootstrapped, pretty theme with a dashboard (using [Creative](https://startbootstrap.com/themes/creative/) and [SB Admin 2](https://startbootstrap.com/themes/sb-admin-2/))
- [ ] User data from signup stored in MySQL Database
- [ ] Login page that checks MySQL Database with credentials
- [ ] Error handling
- [ ] Billing using Stripe for subscriptions