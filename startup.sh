#!/bin/bash
python manage.py collectstatic --noinput && gunicorn --workers 2 Kanban_ui.wsgi:application
