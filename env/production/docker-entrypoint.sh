#!/usr/bin/dumb-init /bin/sh

python manage.py migrate --noinput
echo "Starting gunicorn...."
gunicorn pelocal_chsbc.wsgi:application --bind unix:///dev/shm/gunicorn.sock --worker-tmp-dir /dev/shm --worker-class gevent --access-logfile "-" --workers $NUM_WORKERS --max-requests $MAX_REQUESTS --keep-alive $KEEP_ALIVE_TIMEOUT --env PYTHONUNBUFFERED=1
