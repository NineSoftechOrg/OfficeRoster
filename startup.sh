

#!/bin/sh
# Ensure the Python environment is set up correctly
python -m pip install --upgrade pip
pip install -r requirements.txt
# Apply database migrations
python manage.py migrate --noinput
# Collect static files
python manage.py collectstatic --noinput

# Start the application using gunicorn
python manage.py runserver
