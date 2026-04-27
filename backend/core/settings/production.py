from .base import *

DEBUG = False

# Make sure ALLOWED_HOSTS is appropriately set in production
# Also configure CORS securely
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
