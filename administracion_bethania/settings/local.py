# administracion_bethania/settings/local.py
import os
from dotenv import load_dotenv
from .base import *  # noqa

# Cargar .env.local (si no existe, no rompe)
load_dotenv(BASE_DIR / ".env.local")

DEBUG = env_bool("DEBUG", True)
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "127.0.0.1,localhost")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "http://127.0.0.1,http://localhost")

# Opcional: django-debug-toolbar
if env_bool("ENABLE_DEBUG_TOOLBAR", False):
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = env_list("INTERNAL_IPS", "127.0.0.1")

# Logs útiles en dev
print(f"[DEV] BASE_DIR={BASE_DIR}")
print(f"[DEV] GOOGLE_CREDENTIALS={GOOGLE_CREDENTIALS}")

