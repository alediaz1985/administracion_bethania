# administracion_bethania/settings/production.py
from .base import *

DEBUG = False  # forzado en prod
assert SECRET_KEY and SECRET_KEY != 'django-insecure-change-me', "SECRET_KEY es obligatorio en producción"
assert ALLOWED_HOSTS, "ALLOWED_HOSTS es obligatorio en producción"

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", True)
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", True)
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))  # subilo cuando tengas HTTPS estable
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", False)
