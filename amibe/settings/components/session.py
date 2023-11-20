import os
SESSION_ENGINE = os.environ.get('SESSION_ENGINE', default='django.contrib.sessions.backends.db')
