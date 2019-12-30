FROM python:3.7

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

ADD ./setup_app /setup_app
ADD ./models /models
ADD ./services/NotificationService /services/NotificationService
ADD ./action/notification_action.py /action/notification_action.py
ADD ./data_access/notification_db.py /data_access/notification_db.py

WORKDIR /services/NotificationService

EXPOSE 5002
CMD [ "gunicorn", "-c", "gunicorn_config.py", "main_notification:app" ]