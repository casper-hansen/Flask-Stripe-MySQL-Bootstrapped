# docker-flask-startup-template
Serving a pretty bootstrapped frontend with login page and payment integration. Using docker, flask and stripe in Python.

# Installation

1. Install Python (3.7 was used for this project)
2. Install the package requirements `pip install requirements.txt`
3. Install MySQL server and start it
4. Configure your connector in `backend/db_access.py`

```python
conn = connect(
    host="localhost",
    port='5001',
    user="root",
    passwd="rootpw"
)
```

# Technologies and features

- [x] Python & MySQL Database
- [x] Simplistic REST API with Flask
- [x] Flask Serving Frontend, using MySQL Database
- [x] Reusing HTML files, including scripts, for performance
- [ ] User data from signup stored in MySQL Database
- [ ] Login page that checks MySQL Database with credentials
- [ ] Error handling
- [ ] Billing using Stripe for subscriptions