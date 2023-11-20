import os
from dotenv import load_dotenv


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

load_dotenv(os.path.join(BASE_DIR, '.env'))

APP_NAME = os.environ.get('APP_NAME')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

DEBUG = os.environ.get('DEBUG', False)
# DEBUG = False
DJANGO_ENV = os.environ.get('DJANGO_ENV')

ALLOWED_HOSTS = ['*',]

THIRD_PARTY_APPS = [
    #'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    # 'django.contrib.sites',
    'allauth',
    # 'allauth.account',

    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third Party
    #'django_extensions',
    #'django_filters',
    #'pgcrypto',
    'captcha',

    # celery
    'django_celery_results',
    'django_celery_beat',
    'celery_progress',
    # drf modules that we use
    #'rest_framework',

]

LOCAL_APPS = [
    'apps.authentication',
    'apps.gym_hub',
]

INSTALLED_APPS = THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'allauth.account.middleware.AccountMiddleware',
    # 'allauth.account.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

#    'corsheaders.middleware.CorsPostCsrfMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django_structlog.middlewares.RequestMiddleware',
]

#if DEBUG or DJANGO_ENV == 'uat':
#    UAT_MIDDLEWARE = [
#       'corsheaders.middleware.CorsMiddleware',
#        # 'drf_api_logger.middleware.api_logger_middleware.APILoggerMiddleware',
#        # 'pelocal_b2b_backend.middleware.APILoggingMiddleware',
#    ]
#    MIDDLEWARE = MIDDLEWARE + UAT_MIDDLEWARE
#    INSTALLED_APPS += ['corsheaders']
#    CORS_ALLOWED_ORIGINS = [
#        "http://localhost:3000",
#    ]
#else:
#    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS')
#
#    if DJANGO_ENV in ['uat', 'production']:
 #       ADMINS = [x.split(':') for x in os.environ.get('DJANGO_ADMINS')]
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]


ROOT_URLCONF = 'amibe.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django_settings_export.settings_export',
            ],
            'libraries': {
            },
        },
    },
]


WSGI_APPLICATION = 'amibe.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # NOTE: Do not uncomment. For now we want to keep our signup process simple
    #       and hence we should allow setting up simple password.
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

TIME_ZONE = 'Asia/Kolkata'
# TIME_ZONE='UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATICFILES_DIRS = [
    os.path.join("%s" % BASE_DIR, "static"),
]
# STATIC_ROOT = os.path.join(f"{BASE_DIR}", "static")


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = '/static/'
# STATICFILES_DIRS = [
#     os.path.join("%s" % BASE_DIR, "static"),

# ]

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = 'media/'

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

AUTHENTICATION_CLASSES = (
    'allauth.account.auth_backends.AuthenticationBackend',
    # ... other authentication classes ...
)



# Starting with Django-3.2 the default will be BigAutoField if not specified
# We need to override to avoid generation of any new migration for previous
# models.
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# FILE_LOG = False

RECAPTCHA_PUBLIC_KEY = '6LeGynQnAAAAAJh7cUaEPU2I1-9xStrOYfRBSWWL'
RECAPTCHA_PRIVATE_KEY = '6LeGynQnAAAAAKsigsQ7xOqiQZXpZs2IG5zfc4Zq'

AUTH_USER_MODEL = "authentication.User"

# FILE_UPLOAD_MAX_MEMORY_SIZE=''
# SESSION_COOKIE_AGE=600