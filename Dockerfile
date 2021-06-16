FROM python:3.6

RUN touch /var/log/cron.log
RUN apt-get -y update && apt-get -y install cron
CMD cron && tail -f /var/log/cron.log

COPY web_application/argon-dashboard-django/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY web_application/argon-dashboard-django/manage.py manage.py
COPY web_application/argon-dashboard-django/app app
COPY web_application/argon-dashboard-django/authentication authentication
COPY web_application/argon-dashboard-django/core core

RUN python manage.py makemigrations
RUN python manage.py migrate

EXPOSE 5005
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
