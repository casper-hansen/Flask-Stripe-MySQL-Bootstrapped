FROM python:3.7

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

ADD ./setup_app /setup_app
ADD ./models /models
ADD ./services/UserService /services/UserService
ADD ./action/user_action.py /action/user_action.py
ADD ./data_access/user_db.py /data_access/user_db.py

WORKDIR /services/UserService

EXPOSE 5003
CMD [ "gunicorn", "-c", "gunicorn_config.py", "main_user:app" ]