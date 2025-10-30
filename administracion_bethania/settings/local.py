import os
from pathlib import Path
from dotenv import load_dotenv

# ============================================================
# 1️⃣ Definir BASE_DIR y cargar .env.local antes de importar base.py
# ============================================================
# Este archivo está en administracion_bethania/settings/local.py
# Subimos dos niveles hasta la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parents[2]

# Cargar variables desde .env.local
env_path = BASE_DIR / ".env.local"
if env_path.exists():
    load_dotenv(env_path)
    print(f"[DEV] Cargando variables desde {env_path}")
else:
    print("[DEV] ⚠️ No se encontró .env.local")

# ============================================================
# 2️⃣ Importar todo lo de base.py (ya con el entorno cargado)
# ============================================================
from .base import *  # noqa

# ============================================================
# 3️⃣ Configuración específica del entorno LOCAL
# ============================================================
DEBUG = env_bool("DEBUG", True)
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "127.0.0.1,localhost")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "http://127.0.0.1,http://localhost")

LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "es-ar")
TIME_ZONE = os.getenv("TIME_ZONE", "America/Argentina/Buenos_Aires")
USE_I18N = True
USE_TZ = True

# ============================================================
# Google / Drive / Sheets
# ============================================================
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS", "apps/comprobantes/credentials.json")
COMPROBANTES_SHEET_ID = os.getenv("COMPROBANTES_SHEET_ID", "")
COMPROBANTES_SHEET_TAB = os.getenv("COMPROBANTES_SHEET_TAB", "")
COMPROBANTES_SHEET_RANGE = os.getenv("COMPROBANTES_SHEET_RANGE", "A:E")

# ============================================================
# Base de datos (local con remoto)
# ============================================================
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

# ============================================================
# Debug toolbar opcional
# ============================================================
if env_bool("ENABLE_DEBUG_TOOLBAR", False):
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = env_list("INTERNAL_IPS", "127.0.0.1")

# ============================================================
# Logs de verificación en consola
# ============================================================
print(f"[DEV] BASE_DIR={BASE_DIR}")
print(f"[DEV] GOOGLE_CREDENTIALS={GOOGLE_CREDENTIALS}")
print(f"[DEV] DB_HOST={DATABASES['default']['HOST']}  DB_PORT={DATABASES['default']['PORT']}")
print(f"[DEV] SHEET_ID={COMPROBANTES_SHEET_ID}")
print(f"[DEV] SHEET_TAB={COMPROBANTES_SHEET_TAB}")
print(f"[DEV] SHEET_RANGE={COMPROBANTES_SHEET_RANGE}")
