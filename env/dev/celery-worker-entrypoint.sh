#!/usr/bin/dumb-init /bin/sh

# Sleep for 10 seconds to wait for rabbitmq to start
sleep 10

# rm /run/celerybeat.pid
python -m celery -A pelocal_chsbc beat -l debug -S django_celery_beat.schedulers:DatabaseScheduler  --pidfile /run/celerybeat.pid &
# python -m celery -A pelocal beat -l DEBUG --pidfile /var/run/celerbeat.pid -s /var/run/celerybeat-schedule &
python -m celery -A pelocal_chsbc --beat -l DEBUG flower --basic_auth=${FLOWER_USER}:${FLOWER_PASSWORD} &
python -m celery -A pelocal_chsbc worker -l DEBUG -c 3 -E -Q high_priority,rm_celery_2
