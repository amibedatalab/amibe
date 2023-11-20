import os
from celery import Celery
from django.apps import apps
from kombu import Exchange, Queue

# add rm pelocal project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amibe.settings')
app = Celery('pelocal_chsbc')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])

app.conf.task_queues = (
    Queue('high_priority', Exchange('rm_high'),
          routing_key='rm_high', consumer_arguments={'x-priority': 10}),
    Queue('celery', Exchange('celery'), routing_key='celery',
          consumer_arguments={'x-priority': 9}),
)

app.conf.task_default_queue = 'celery'

# Specify which queues the tasks fired should go to.
app.conf.task_routes = {
    'chsbc_hub.tasks.*': {
        'queue': 'high_priority',
        'routing_key': 'rm_high',
    }
}

task_default_exchange = 'celery'
task_default_exchange_type = 'celery'
task_default_routing_key = 'celery'

CELERY_IMPORTS = ('chsbc_hub.tasks')
