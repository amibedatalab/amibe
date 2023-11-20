#!/usr/bin/dumb-init /bin/sh

python manage.py migrate --noinput
echo "Starting gunicorn...."
gunicorn pelocal_chsbc.wsgi:application --bind unix:///dev/shm/gunicorn.sock --worker-tmp-dir /dev/shm --worker-class gevent --access-logfile "-" --workers=2 --max-requests=10 --keep-alive=60 --env PYTHONUNBUFFERED=1
