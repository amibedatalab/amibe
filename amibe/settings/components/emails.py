import base64
import os
# EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND')
# EMAIL_USE_TLS = True
# EMAIL_HOST = os.environ.get('EMAIL_HOST')
# EMAIL_PORT = os.environ.get('EMAIL_PORT')
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_port')
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_DEBUG = True  # Enable debugging


# TODO: Pick from environment
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_TIMEOUT = 120
SERVER_EMAIL = f"admin@{DOMAIN_NAME}"
DEFAULT_FROM_EMAIL = f"support@{DOMAIN_NAME}"
NOREPLY_EMAIL = f"{APP_NAME}<noreply@{DOMAIN_NAME}>"
CONTACTUS_EMAIL = f"contact@{DOMAIN_NAME}"
SUPPORT_EMAIL = f"support@{DOMAIN_NAME}"

# ALERT EMAIL SEND
ALERT_FROM_EMAIL = os.environ.get('ALERT_FROM_EMAIL')
ALERT_RECIPIENT_LIST = list(os.environ.get('ALERT_RECIPIENT_LIST').split(','))
ALERT_EMAIL_PASSWORD = base64.b64decode(os.environ.get('ALERT_EMAIL_PASSWORD')).decode('utf-8')