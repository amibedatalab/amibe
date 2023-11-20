# Configure security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True
SERVER = False

# This tells Django that your application is behind a reverse proxys
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content-Security-Policy headers
# CSP_DEFAULT_SRC = "self"
# CSP_STYLE_SRC = "self' 'unsafe-inline"
# CSP_SCRIPT_SRC = "self' 'unsafe-inline' 'unsafe-eval' https://ajax.googleapis.com"
# CSP_IMG_SRC = "self' data:"
# CSP_FONT_SRC = "self"
# CSP_CONNECT_SRC = "self"
# CSP_FRAME_SRC = "none"
# CSP_BASE_URI = "self"
# CSP_OBJECT_SRC = "none"
# CSP_FORM_ACTION = "self"
# CSP_BLOCK_ALL_MIXED_CONTENT = True
# CSP_UPGRADE_INSECURE_REQUESTS = True

# Permissions-Policy headers
PERMISSIONS_POLICY = "geolocation=()"

