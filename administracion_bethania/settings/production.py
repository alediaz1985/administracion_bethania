# administracion_bethania/settings/production.py
import os
from dotenv import load_dotenv
from .base import *

# Cargar .env.prod
load_dotenv(os.path.join(BASE_DIR, '.env.prod'), override=True)

DEBUG = False

# Hosts y CSRF desde .env
ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', '')
CSRF_TRUSTED_ORIGINS = [o for o in env_list('CSRF_TRUSTED_ORIGINS', '')]

# Seguridad (ajusta según tu HTTPS)
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', True)
CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', True)
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '0'))  # subilo a 31536000 cuando tengas HTTPS estable
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', False)
SECURE_HSTS_PRELOAD = env_bool('SECURE_HSTS_PRELOAD', False)
SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', False)  # True si forzás HTTPS

# WhiteNoise para estáticos en producción (si no usas Nginx/Apache para /static/)
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Logging básico a consola
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
