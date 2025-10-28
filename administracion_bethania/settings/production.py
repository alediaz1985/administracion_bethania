# administracion_bethania/settings/production.py
import os
from dotenv import load_dotenv
from .base import *  # noqa

# Cargar variables de entorno de producción
load_dotenv(BASE_DIR / ".env.production")

# --- Básico ---
DEBUG = env_bool("DEBUG", False)
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "dalisserver1.duckdns.org")
CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    "https://dalisserver1.duckdns.org,http://dalisserver1.duckdns.org",
)

# Misma DB que local (viene de base.py vía variables .env)
# Ajuste de conexiones persistentes en prod
DATABASES["default"]["CONN_MAX_AGE"] = int(os.getenv("DB_CONN_MAX_AGE", "120"))

# --- Archivos estáticos ---
STATIC_ROOT = str(BASE_DIR / "staticfiles")  # donde va collectstatic
ENABLE_WHITENOISE = env_bool("ENABLE_WHITENOISE", True)
if ENABLE_WHITENOISE:
    # Inserta WhiteNoise después de SecurityMiddleware
    MIDDLEWARE = (
        ["django.middleware.security.SecurityMiddleware"]
        + ["whitenoise.middleware.WhiteNoiseMiddleware"]
        + MIDDLEWARE[1:]
    )
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --- Seguridad (activar en HTTPS real) ---
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", False)
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", SECURE_SSL_REDIRECT)
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", SECURE_SSL_REDIRECT)
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0" if not SECURE_SSL_REDIRECT else "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", False)

# Detrás de proxy (Nginx/Cloudflare) que setea X-Forwarded-Proto
BEHIND_REVERSE_PROXY = env_bool("BEHIND_REVERSE_PROXY", False)
if BEHIND_REVERSE_PROXY:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True

# --- Logging simple a consola ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": os.getenv("DJANGO_LOG_LEVEL", "INFO")},
}

# Pequeño rastro útil en arranque
print(f"[PROD] Cargando: {BASE_DIR / '.env.production'}")
print(f"[PROD] DB_HOST= {DATABASES['default']['HOST']}  DB_PORT= {DATABASES['default']['PORT']}")
