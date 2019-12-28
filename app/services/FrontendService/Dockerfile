FROM python:3.7

COPY ./../../../requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

ADD ./../../setup_app /setup_app
ADD ./../../models /models
ADD ./../../static /static
ADD ./../../templates /templates
ADD ./../FrontendService /services/FrontendService
ADD ./../../action/frontend_action.py /action/frontend_action.py

WORKDIR /services/FrontendService

EXPOSE 5000
CMD [ "gunicorn", "-c", "gunicorn_config.py", "main_frontend:app" ]