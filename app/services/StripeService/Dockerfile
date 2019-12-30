FROM python:3.7

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

ADD ./setup_app /setup_app
ADD ./models /models
ADD ./services/StripeService /services/StripeService
ADD ./action/stripe_action.py /action/stripe_action.py
ADD ./data_access/stripe_db.py /data_access/stripe_db.py

WORKDIR /services/StripeService

EXPOSE 5004
CMD [ "gunicorn", "-c", "gunicorn_config.py", "main_stripe:app" ]