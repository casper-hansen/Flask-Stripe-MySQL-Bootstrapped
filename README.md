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