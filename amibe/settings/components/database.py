# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

# Should match with the settings in docker-compose:db service settings
import  base64

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQL_DB'),
        'USER': os.getenv('MYSQL_USER'),
        'PASSWORD': os.getenv('MYSQL_PASSWORD'), # HACK ::  please remove this
        'HOST': os.getenv('MYSQL_HOST'),
        'PORT': os.getenv('MYSQL_PORT')
    },
   'readonly': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQL_DB'),
        'USER': os.getenv('MYSQL_USER'),
        'PASSWORD': os.getenv('MYSQL_PASSWORD'), # HACK ::  please remove this
        'HOST': os.getenv('MYSQL_HOST'),
        'PORT': os.getenv('MYSQL_PORT'),
    },
}


# DATABASE_ROUTERS = ['pelocal_chsbc.db_router.DatabaseRouter']
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': os.getenv('MYSQL_DB'),
#         'USER': os.getenv('MYSQL_USER'),
#         'PASSWORD': os.getenv('MYSQL_PASSWORD'), # HACK ::  please remove this
#         'HOST': os.getenv('MYSQL_HOST'),
#         'PORT': os.getenv('MYSQL_PORT'),
#     },
#     'readonly': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': os.getenv('MYSQL_DB'),
#         'USER': os.getenv('MYSQL_USER'),
#         'PASSWORD': os.getenv('MYSQL_PASSWORD'), # HACK ::  please remove this
#         'HOST': os.getenv('MYSQL_HOST'),
#         'PORT': os.getenv('MYSQL_PORT'),
#     },
# }


# DATABASE_ROUTERS = ['pelocal_chsbc.db_router.DatabaseRouter']
