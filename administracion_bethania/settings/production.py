"""
Configuración de PRODUCCIÓN
---------------------------
- Carga .env.production (fallback a .env) ANTES de importar base.py
- Seguridad reforzada (SSL/HSTS/Cookies)
- DB remota MariaDB
- WhiteNoise (o S3 opcional)
- Logging sobrio + Sentry opcional
"""
from .base import *
import os
from pathlib import Path
from dotenv import load_dotenv

# 1) Rutas y carga de entorno (antes de importar base.py)
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env.production", override=True)
load_dotenv(BASE_DIR / ".env", override=False)

# 2) Importar configuración común
from .base import *  # noqa: F401,F403

# 3) Flags generales
DEBUG = False
# SECRET_KEY obligatorio en prod (si falta, que explote)
SECRET_KEY = os.environ["SECRET_KEY"]


ALLOWED_HOSTS = [
    "vps-5435089-x.dattaweb.com",
    "127.0.0.1",
    "localhost",
]

CSRF_TRUSTED_ORIGINS = [
    "http://vps-5435089-x.dattaweb.com",
    "https://vps-5435089-x.dattaweb.com",
]

# 4) Seguridad / SSL
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)

SESSION_COOKIE_SECURE = False

CSRF_COOKIE_SECURE = False

# HSTS (activar en cuanto tengas HTTPS estable)
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", True)
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", True)

# Si hay proxy (Nginx/ELB/Cloudflare) que setea X-Forwarded-Proto
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# 5) Base de datos (MariaDB remota)
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.mysql"),
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ["DB_HOST"],
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": os.getenv("DB_CHARSET", "utf8mb4"),
            "init_command": os.getenv(
                "DB_INIT_COMMAND",
                "SET sql_mode='STRICT_TRANS_TABLES'"
            ),
            "connect_timeout": int(os.getenv("DB_CONN_TIMEOUT", "10")),
            # SSL condicional (si DB_SSL=1 y DB_SSL_CA presente)
            **(
                {"ssl": {"ca": os.getenv("DB_SSL_CA")}}
                if env_bool("DB_SSL", False) and os.getenv("DB_SSL_CA")
                else {}
            ),
        },
        "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),  # pooling
    }
}

# 6) Cache (Redis opcional)
REDIS_URL = os.getenv("REDIS_URL", "")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }

# 7) Email (SMTP real)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.sendgrid.net")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@tu-dominio.com")
SERVER_EMAIL = os.getenv("SERVER_EMAIL", DEFAULT_FROM_EMAIL)

# 8) Archivos estáticos
USE_WHITENOISE = env_bool("USE_WHITENOISE", True)
STATIC_ROOT = str((BASE_DIR / "static_collected").resolve())

if USE_WHITENOISE:
    INSTALLED_APPS = ["whitenoise.runserver_nostatic"] + INSTALLED_APPS  # noqa: F405
    MIDDLEWARE.insert(  # noqa: F405
        MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,  # noqa: F405
        "whitenoise.middleware.WhiteNoiseMiddleware",
    )
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Alternativa S3 (si aplica)
# STORAGES = {
#     "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
#     "staticfiles": {"BACKEND": "storages.backends.s3boto3.S3ManifestStaticStorage"},
# }
# AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")

# 9) Admins / errores
# Formato: "Nombre|correo,Otra Persona|correo2"
raw_admins = env_list("ADMINS", "")
ADMINS = []
for item in raw_admins:
    if "|" in item:
        name, email = item.split("|", 1)
        ADMINS.append((name, email))

# 10) Logging sobrio
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

# 11) Sentry (opcional)
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.2")),
    )
