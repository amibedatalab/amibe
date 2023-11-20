from os import environ

rabbitmq_host = environ.get('RABBITMQ_HOST')
rabbitmq_user = environ.get('RABBITMQ_DEFAULT_USER')
rabbitmq_pass = environ.get('RABBITMQ_DEFAULT_PASSWORD')
rabbitmq_vhost = environ.get('RABBITMQ_DEFAULT_VHOST')

rabbitmq_port = 5672  # env('RABBITMQ_PORT')
CELERY_BROKER_URL = f"amqp://guest:guest@localhost:5672/chsbc"
print(CELERY_BROKER_URL)
CELERY_RESULT_BACKEND = 'django-db'
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_BROKER_CONNECTION_TIMEOUT = 30
CELERY_BROKER_HEARTBEAT = None
# NOTE: Do not set it to 1, which causes the tasks to not even launch
#       Setting it to None does work but that means the connection will
#       be opened and closed for every use.
CELERY_BROKER_POOL_LIMIT = None

#progressive bar config
CELERY_ACCEPT_CONTENT=['json']
CELERY_TASK_SERIALIZER='json'