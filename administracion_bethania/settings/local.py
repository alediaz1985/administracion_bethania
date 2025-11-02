"""
Configuración LOCAL (Desarrollo)
--------------------------------
Cargando variables desde .env.local, y hereda toda la configuración
común desde base.py.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from .base import *  # noqa: F401,F403

# ============================================================
# 1) Directorio base y carga del entorno
# ============================================================
BASE_DIR = Path(__file__).resolve().parents[2]

# Cargar primero .env.local (si existe), luego fallback a .env
load_dotenv(BASE_DIR / ".env.local", override=True)
load_dotenv(BASE_DIR / ".env", override=False)

# ============================================================
# 2) Parámetros generales
# ============================================================
DEBUG = env_bool("DEBUG", True)

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "127.0.0.1,localhost")
CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    "http://127.0.0.1:8000,http://localhost:8000",
)

LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "es-ar")
TIME_ZONE = os.getenv("TIME_ZONE", "America/Argentina/Buenos_Aires")
USE_I18N, USE_TZ = True, True

# ============================================================
# 3) Base de datos (usa tus credenciales remotas)
# ============================================================
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.mysql"),
        "NAME": os.getenv("DB_NAME", ""),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": os.getenv("DB_CHARSET", "utf8mb4"),
            "init_command": os.getenv(
                "DB_INIT_COMMAND",
                "SET sql_mode='STRICT_TRANS_TABLES'"
            ),
            "connect_timeout": int(os.getenv("DB_CONN_TIMEOUT", "10")),
        },
        "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "0")),
    }
}

# ============================================================
# 4) Email / Cache / Archivos
# ============================================================
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "local-unique",
    }
}

# ============================================================
# 5) WhiteNoise (si lo habilitás en .env)
# ============================================================
if env_bool("ENABLE_WHITENOISE", False):
    INSTALLED_APPS = ["whitenoise.runserver_nostatic"] + INSTALLED_APPS  # noqa: F405
    MIDDLEWARE.insert(
        MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,  # noqa: F405
        "whitenoise.middleware.WhiteNoiseMiddleware",
    )
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ============================================================
# 6) Debug Toolbar (si ENABLE_DEBUG_TOOLBAR=true)
# ============================================================
if env_bool("ENABLE_DEBUG_TOOLBAR", False):
    INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE  # noqa: F405
    INTERNAL_IPS = env_list("INTERNAL_IPS", "127.0.0.1")

# ============================================================
# 7) Logging limpio a consola
# ============================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "DEBUG" if DEBUG else "INFO"},
}
