#!/bin/bash

sleep 10
python -m celery -A pelocal_chsbc worker -l DEBUG -c 3 -E -Q high_priority,celery