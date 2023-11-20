CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        # 'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        # 'LOCATION': f"{os.environ.get('MEMCACHED_HOST')}"
        #             f":{os.environ.get('MEMCACHED_PORT')}",
        # 'OPTIONS': {
        #     'binary': False,
        #     'behaviors': {
        #         'ketama': True,
        #         'remove_failed': 1,
        #         'retry_timeout': 1,
        #         'dead_timeout': 60
        #     }
        # }
    }
}
