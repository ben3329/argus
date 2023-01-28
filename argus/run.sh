#!/bin/bash
echo "root:${DJANGO_SUPERUSER_PASSWORD}" | chpasswd
service ssh start
wait-for-it database:3306 -- python manage.py migrate
python manage.py makemigrations monitoring
python manage.py migrate monitoring
python manage.py createsuperuser --noinput
python manage.py runserver 0.0.0.0:8080