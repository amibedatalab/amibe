import os 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
LOCAL_APPS = [
    'apps.authentication',
    'apps.chsbc_hub',
]
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(module)s:%(funcName)s:'
                      '%(lineno)s %(processName)s %(process)d] %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s:%(funcName)s:%(lineno)s::'
                      '%(message)s'
        }
    },
    'filters': {
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'file':{
          'level': 'INFO',
          'class': 'logging.FileHandler',
          'filename': os.path.join(BASE_DIR, "server_logs/info_file.log"),
          'formatter': 'verbose',

        }
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'INFO',
        }
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
