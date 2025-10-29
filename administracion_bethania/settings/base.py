# administracion_bethania/settings/base.py
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]  # .../administracion_bethania/

# Helpers .env
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
    return path if os.path.isabs(path) else str(BASE_DIR / path)

# No cargamos .env acá: lo hará cada módulo (local/production)
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me')

# Apps comunes
INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "crispy_forms", "crispy_bootstrap4",
    "apps.administracion", 
    "apps.autenticacion",
    "apps.administracion_alumnos", 
    "apps.dashboard",
    "apps.documentos",
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
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR / 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]



WSGI_APPLICATION = "administracion_bethania.wsgi.application"

# DB: los valores concretos los toma cada entorno desde su .env.*
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.mysql"),
        "NAME": os.getenv("DB_NAME", "hbethania"),
        "USER": os.getenv("DB_USER", "admin_remoto"),
        "PASSWORD": os.getenv("DB_PASSWORD", "admin123_remoto"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3307"),
        "OPTIONS": {
            "charset": os.getenv("DB_CHARSET", "utf8mb4"),
            "init_command": os.getenv("DB_INIT_COMMAND", "SET sql_mode='STRICT_TRANS_TABLES'"),
            "connect_timeout": int(os.getenv("DB_CONN_TIMEOUT", "10")),
            **(
                {"ssl": {"ca": os.getenv("DB_SSL_CA")}}
                if env_bool("DB_SSL", False) and os.getenv("DB_SSL_CA")
                else {}
            ),
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "es-ar")
TIME_ZONE = os.getenv("TIME_ZONE", "America/Argentina/Buenos_Aires")
USE_I18N, USE_TZ = True, True

STATIC_URL = '/static/'
STATICFILES_DIRS = [str(BASE_DIR / "static")]  # STATIC_ROOT sólo en prod
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = str(BASE_DIR / "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "iniciar_sesion"
CRISPY_TEMPLATE_PACK = "bootstrap4"

# Google / Drive / Rutas
GOOGLE_CREDENTIALS_ALUMNOS = env_path("GOOGLE_CREDENTIALS_ALUMNOS", "apps/administracion_alumnos/credentials.json")
GOOGLE_CREDENTIALS = env_path("GOOGLE_CREDENTIALS", "apps/documentos/credentials.json")
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "")
DRIVE_FOLDER_ID_ALUMNOS = os.getenv("DRIVE_FOLDER_ID_ALUMNOS", "")
ARCHIVOS_DIR = env_path("ARCHIVOS_DIR", "media/documentos")
FOTO_PERFIL_ESTUDIANTE_DIR = env_path("FOTO_PERFIL_ESTUDIANTE_DIR", "media/documentos/fotoPerfilEstudiante")
FOTO_ESTUDIANTE_DIR = env_path("FOTO_ESTUDIANTE_DIR", "media/administracion_alumnos/descargados")

# Datos de la institución (para PDFs, headers, etc.)
INSTITUCION_NOMBRE = os.getenv("INSTITUCION_NOMBRE", "")
INSTITUCION_DIRECCION = os.getenv("INSTITUCION_DIRECCION", "")
INSTITUCION_TELEFONO = os.getenv("INSTITUCION_TELEFONO", "")
INSTITUCION_EMAIL = os.getenv("INSTITUCION_EMAIL", "")
INSTITUCION_LOGO_PATH = env_path("INSTITUCION_LOGO_PATH", "static/img/logo.png")
INSTITUCION_FOTO_DIR = env_path("INSTITUCION_FOTO_DIR", "media/documentos/fotoPerfilEstudiante")

# ============================================================
# ⚙️ CONFIGURACIÓN DE SESIONES
# ============================================================

# Cierra la sesión al cerrar el navegador
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Tiempo máximo de sesión (1 hora)
SESSION_COOKIE_AGE = 3600

# Renueva el tiempo si el usuario sigue activo
SESSION_SAVE_EVERY_REQUEST = True
