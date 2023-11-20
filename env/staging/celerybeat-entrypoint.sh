#!/bin/bash

sleep 10
python -m celery -A pelocal_chsbc beat -l debug -S django_celery_beat.schedulers:DatabaseScheduler  --pidfile /dev/shm/celerybeat.pid