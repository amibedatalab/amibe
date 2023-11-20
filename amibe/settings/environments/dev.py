# DEBUG = True
# # For now set ALLOWED_HOSTS to *. In k8s the IP address is from vpc-cni
# # networking for health checks made to the pod. This will be the IP allocated
# # to the pod. Hence the health check would fail for the health check requests
# # made from AWS ALB. To solve this, either we need to put the following
# # package https://github.com/mozmeao/django-allow-cidr to set the CIDR range
# # from which the health checks are allowed or inject the POD_IP in the pod's
# # environment variable and use that in the ALLOWED_HOSTS list.
# # ALLOWED_HOSTS = ['*']
# ALLOWED_HOSTS = ['*']
# DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# PG_CALLBACK_URL = 'https://rm-api.pelocal.com/dmrc/payment-status'
# DMRC_F_KEY = '5U5cH47pq5gQSRXtFw-dfHbJFfEna2WS96pS4gGt9XQ='

# # Zaakpay API endpoints
# VERIFY_PAYMENT_ENDPOINT = "https://api.zaakpay.com/checkTxn?v=5"
# CREATE_PAYMENT_ENDPOINT = "https://pay.zaakpay.com/pl/api/v1/create"
# INITIATE_REFUND_ENDPOINT = "https://api.zaakpay.com/updateTxn"
# SETTLEMENT_ENPOINT = "https://zaakpay.com/api/v2/getSettlementReport"