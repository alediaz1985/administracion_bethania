# administracion_bethania/settings/local.py
import os
from dotenv import load_dotenv
from .base import *  # noqa

# =========================
# Cargar variables de .env.local (si falta, no rompe)
# =========================
load_dotenv(BASE_DIR / ".env.local")

# =========================
# Básico de Django (LOCAL)
# =========================
DEBUG = env_bool("DEBUG", True)
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "127.0.0.1,localhost")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "http://127.0.0.1,http://localhost")

LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "es-ar")
TIME_ZONE = os.getenv("TIME_ZONE", "America/Argentina/Buenos_Aires")
USE_I18N = True
USE_TZ = True

# =========================
# Debug toolbar (opcional)
# =========================
if env_bool("ENABLE_DEBUG_TOOLBAR", False):
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = env_list("INTERNAL_IPS", "127.0.0.1")

# =========================
# Archivos estáticos y media (dev)
# =========================
# En dev, runserver sirve estáticos; WhiteNoise desactivado
ENABLE_WHITENOISE = env_bool("ENABLE_WHITENOISE", False)

# Si en base.py usás rutas por defecto, no hace falta tocar.
# Si querés forzar rutas locales:
# STATIC_URL = "/static/"
# MEDIA_URL = "/media/"
# STATIC_ROOT = BASE_DIR / "staticfiles"
# MEDIA_ROOT = BASE_DIR / "media"

# =========================
# Google / credenciales extra
# =========================
# Estas variables vienen de .env.local si las definiste
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS", GOOGLE_CREDENTIALS)
GOOGLE_CREDENTIALS_ALUMNOS = os.getenv("GOOGLE_CREDENTIALS_ALUMNOS", None)

# =========================
# FORZAR DATABASES desde .env.local
# (evita que quede el config de base/.env)
# =========================
DATABASES["default"] = {
    "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.mysql"),
    "NAME": os.getenv("DB_NAME", ""),
    "USER": os.getenv("DB_USER", ""),
    "PASSWORD": os.getenv("DB_PASSWORD", ""),
    "HOST": os.getenv("DB_HOST", "127.0.0.1"),
    "PORT": os.getenv("DB_PORT", "3306"),
    "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "0")),
    "OPTIONS": {
        "charset": os.getenv("DB_CHARSET", "utf8mb4"),
        "init_command": os.getenv("DB_INIT_COMMAND", "SET sql_mode='STRICT_TRANS_TABLES'"),
    },
}

# =========================
# Prints útiles en consola (dev)
# =========================
print(f"[DEV] BASE_DIR={BASE_DIR}")
print(f"[DEV] GOOGLE_CREDENTIALS={GOOGLE_CREDENTIALS}")
print(f"[DEV] DB_HOST={DATABASES['default']['HOST']}  DB_PORT={DATABASES['default']['PORT']}")
