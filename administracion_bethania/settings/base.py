# administracion_bethania/settings/base.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # .../administracion_bethania/

# -------------------------------------------------
# Helpers .env (cada entorno carga su .env aparte)
# -------------------------------------------------
def env_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key, str(default))
    return str(val).strip().lower() in ("1", "true", "t", "yes", "y", "si", "sí")

def env_list(key: str, default: str = "") -> list[str]:
    raw = os.getenv(key, default)
    return [x.strip() for x in raw.split(",") if x.strip()]

def env_path(key: str, default_rel: str | None = None) -> str | None:
    raw = os.getenv(key, "")
    if not raw and default_rel is None:
        return None
    path = raw or (default_rel or "")
    return path if os.path.isabs(path) else str((BASE_DIR / path).resolve())

# -------------------------------------------------
# Core (sin DEBUG/ALLOWED_HOSTS/DATABASES acá)
# -------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-me")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Forms
    "crispy_forms",
    "crispy_bootstrap4",
    "crispy_bootstrap5",
    # Apps propias
    "apps.administracion",
    "apps.autenticacion.apps.AutenticacionConfig",
    "apps.administracion_alumnos",
    "apps.dashboard",
    "apps.comprobantes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "administracion_bethania.middleware.LoginRequiredMiddleware",
    "apps.administracion.middleware.actualizar_cuotas.ActualizarCuotasMiddleware",
]

ROOT_URLCONF = "administracion_bethania.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(BASE_DIR / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "administracion_bethania.wsgi.application"
# ASGI_APPLICATION = "administracion_bethania.asgi.application"  # descomentar si usás ASGI

# -------------------------------------------------
# Auth / Passwords
# -------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------------------------------
# Internacionalización / Zona horaria
# -------------------------------------------------
LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "es-ar")
TIME_ZONE = os.getenv("TIME_ZONE", "America/Argentina/Cordoba")
USE_I18N, USE_TZ = True, True

# -------------------------------------------------
# Static & Media (STATIC_ROOT sólo en production)
# -------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [str(BASE_DIR / "static")]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -------------------------------------------------
# Django Crispy Forms
# -------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = ("bootstrap4", "bootstrap5")
CRISPY_TEMPLATE_PACK = os.getenv("CRISPY_TEMPLATE_PACK", "bootstrap4")

# -------------------------------------------------
# Defaults
# -------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "iniciar_sesion"

# -------------------------------------------------
# Google / Drive / Rutas
# -------------------------------------------------
GOOGLE_CREDENTIALS_ALUMNOS = env_path(
    "GOOGLE_CREDENTIALS_ALUMNOS",
    "apps/administracion_alumnos/credentials.json",
)

# Unificado (antes estaba duplicado)
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS", "apps/comprobantes/credentials.json")
if not os.path.isabs(GOOGLE_CREDENTIALS):
    GOOGLE_CREDENTIALS = str((BASE_DIR / GOOGLE_CREDENTIALS).resolve())

DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "")
DRIVE_FOLDER_ID_ALUMNOS = os.getenv("DRIVE_FOLDER_ID_ALUMNOS", "")
ARCHIVOS_DIR = env_path("ARCHIVOS_DIR", "media/documentos")
FOTO_PERFIL_ESTUDIANTE_DIR = env_path("FOTO_PERFIL_ESTUDIANTE_DIR", "media/documentos/fotoPerfilEstudiante")
FOTO_ESTUDIANTE_DIR = env_path("FOTO_ESTUDIANTE_DIR", "media/administracion_alumnos/descargados")

# Google Sheets (comprobantes)
COMPROBANTES_SHEET_ID    = os.getenv("COMPROBANTES_SHEET_ID", "")
COMPROBANTES_SHEET_TAB   = os.getenv("COMPROBANTES_SHEET_TAB", "")
COMPROBANTES_SHEET_RANGE = os.getenv("COMPROBANTES_SHEET_RANGE", "A:E")

# Orígenes de Drive etiquetados (IDs por entorno)
DRIVE_SOURCES = {
    "comprobantes": {
        "folder_id": os.getenv("DRIVE_FOLDER_COMPROBANTES", ""),
        "dest_subpath": "documentos/comprobantes",  # relativo a MEDIA_ROOT
    },
}

# -------------------------------------------------
# Datos de la institución
# -------------------------------------------------
INSTITUCION_NOMBRE = os.getenv("INSTITUCION_NOMBRE", "")
INSTITUCION_DIRECCION = os.getenv("INSTITUCION_DIRECCION", "")
INSTITUCION_TELEFONO = os.getenv("INSTITUCION_TELEFONO", "")
INSTITUCION_EMAIL = os.getenv("INSTITUCION_EMAIL", "")
INSTITUCION_LOGO_PATH = env_path("INSTITUCION_LOGO_PATH", "static/img/logo.png")
INSTITUCION_FOTO_DIR = env_path("INSTITUCION_FOTO_DIR", "media/documentos/fotoPerfilEstudiante")

# -------------------------------------------------
# Sesiones
# -------------------------------------------------
# Cierra la sesión al cerrar el navegador
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# Tiempo máximo de sesión (1 hora)
SESSION_COOKIE_AGE = 3600
# Renueva el tiempo si el usuario sigue activo
SESSION_SAVE_EVERY_REQUEST = True

# -------------------------------------------------
# Base de datos
# -------------------------------------------------
# Intencionalmente VACÍO en base.py.
# Definilo por completo en:
# - administracion_bethania/settings/local.py
# - administracion_bethania/settings/production.py
# Ejemplo de shape esperado:
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME": "...",
#         "USER": "...",
#         "PASSWORD": "...",
#         "HOST": "...",
#         "PORT": "3306",
#         "OPTIONS": {...},
#         "CONN_MAX_AGE": 0,
#     }
# }
