#!/bin/bash
wait-for-it database:3306 -- python manage.py migrate
python manage.py makemigrations argus
python manage.py migrate argus
python manage.py createsuperuser --noinput
python manage.py runserver 0.0.0.0:8080