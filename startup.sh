#!/bin/bash

# Export environment variables
export DJANGO_SETTINGS_MODULE=Kanban_ui.settings

#install dependencies
pip install -r requirements.txt

python manage.py migrate

python manage.py collectstatic --noinput

gunicorn --workers 2 Kanban_ui.wsgi:application
