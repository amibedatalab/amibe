"""
This is a django-split-settings main file.
For more information read this:
https://github.com/sobolevn/django-split-settings
Default environment is `developement`.
To change settings file:
`DJANGO_ENV=production python manage.py runserver`
"""
from os import environ
from split_settings.tools import optional, include

ENV = (environ.get('DJANGO_ENV') or 'development').lower()
APP_VERSION = environ.get("APP_VERSION") or 'development'
DOMAIN_NAME = environ.get('DOMAIN_NAME')
AUTO_REGISTER_EMAIL_DOMAIN = "pelocal.com"
AUTO_REGISTER_USER_FIRST_NAME = "Anonymous"
AUTO_REGISTER_USER_LAST_NAME = "User"

# NOTE: This is order dependent so make sure to add settings
# appropriately
BASE_SETTINGS = [
    'components/common.py',  # standard django settings
    'components/database.py',  # mysql
    'components/emails.py',  # smtp
    'components/logging.py',  # logger
    'components/caches.py',  # chats settings
    'components/session.py',  # session settings
    'components/drf.py',  # drf settings
    'components/swagger.py',  # debug-toolbar settings
    'components/misc.py',  # miscellaneous settings
    'components/celery.py',  # drf settings
    'components/pinelab.py',  # pinelab settings
    'components/errors.py',
]

if ENV != 'development' and ENV != 'testing':
    BASE_SETTINGS += 'components/aws_storage.py',
    BASE_SETTINGS += 'components/security_headers.py',


# Settings specific to an environment
BASE_SETTINGS += [
    'environments/%s.py' % ENV,
]

# Optionally override some settings for development
if ENV == 'development':
    BASE_SETTINGS += [
        'components/debugtoolbar.py',  # debug-toolbar settings
    ]

# Include settings:
include(*BASE_SETTINGS)

# Settings to export in templates
SETTINGS_EXPORT = [
    'APP_VERSION',
    'APP_NAME',
]
