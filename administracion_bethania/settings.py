# =========================
# settings.py (limpio + .env)
# =========================
import os
from pathlib import Path
from dotenv import load_dotenv

# Base
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Helpers para resolver rutas del .env:
def env_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key, str(default))
    return str(val).strip().lower() in ("1", "true", "t", "yes", "y", "si", "sí")

def env_list(key: str, default: str = "") -> list[str]:
    raw = os.getenv(key, default)
    return [x.strip() for x in raw.split(",") if x.strip()]

def env_path(key: str, default_rel: str | None = None) -> str | None:
    """
    Si el valor del .env es ruta absoluta, la deja.
    Si no, la resuelve relativa a BASE_DIR.
    Si no existe key y default_rel es None, devuelve None.
    """
    raw = os.getenv(key, "")
    if not raw and default_rel is None:
        return None
    path = raw or default_rel or ""
    return path if os.path.isabs(path) else str(BASE_DIR / path)

# =========================
# Seguridad / entorno
# =========================
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me')
DEBUG = env_bool('DEBUG', True)
ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', '127.0.0.1,localhost')

# =========================
# Aplicaciones
# =========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'crispy_forms',
    'crispy_bootstrap4',

    'apps.administracion',
    'apps.autenticacion',
    'apps.administracion_alumnos',
    # 'apps.documentos',
    'apps.dashboard',
]

# =========================
# Middleware
# =========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'administracion_bethania.middleware.LoginRequiredMiddleware',
]

ROOT_URLCONF = 'administracion_bethania.urls'

# =========================
# Templates
# =========================
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

WSGI_APPLICATION = 'administracion_bethania.wsgi.application'

# =========================
# Base de datos
# =========================
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.mysql'),
        'NAME': os.getenv('DB_NAME', 'hbethania'),
        'USER': os.getenv('DB_USER', 'admin_remoto'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'admin123_remoto'),
        'HOST': os.getenv('DB_HOST', 'dalisserver1.duckdns.org'),
        'PORT': os.getenv('DB_PORT', '3307'),
        # Opcional: parámetros extra de MySQL
        # 'OPTIONS': {'charset': 'utf8mb4'},
    }
}

# =========================
# Password validators
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# =========================
# Internacionalización
# =========================
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'es-ar')
TIME_ZONE = os.getenv('TIME_ZONE', 'America/Argentina/Buenos_Aires')
USE_I18N = True
USE_TZ = True

# =========================
# Archivos estáticos / media
# =========================
STATIC_URL = '/static/'
STATICFILES_DIRS = [str(BASE_DIR / 'static')]

# Si desplegás con collectstatic:
# STATIC_ROOT = str(BASE_DIR / 'staticfiles')

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = str(BASE_DIR / 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =========================
# Auth
# =========================
LOGIN_URL = 'iniciar_sesion'

# =========================
# Crispy forms
# =========================
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# =========================
# Google / Drive / Rutas varias (desde .env)
# =========================
# Pueden ser relativas al BASE_DIR en el .env
GOOGLE_CREDENTIALS_ALUMNOS = env_path('GOOGLE_CREDENTIALS_ALUMNOS', 'apps/administracion_alumnos/credentials.json')
GOOGLE_CREDENTIALS = env_path('GOOGLE_CREDENTIALS', 'apps/documentos/credentials.json')

DRIVE_FOLDER_ID = os.getenv('DRIVE_FOLDER_ID', '')
DRIVE_FOLDER_ID_ALUMNOS = os.getenv('DRIVE_FOLDER_ID_ALUMNOS', '')

ARCHIVOS_DIR = env_path('ARCHIVOS_DIR', 'media/documentos')
FOTO_PERFIL_ESTUDIANTE_DIR = env_path('FOTO_PERFIL_ESTUDIANTE_DIR', 'media/documentos/fotoPerfilEstudiante')
FOTO_ESTUDIANTE_DIR = env_path('FOTO_ESTUDIANTE_DIR', 'media/administracion_alumnos/descargados')

# Logs/prints sólo si DEBUG
if DEBUG:
    print(f"[DEBUG] GOOGLE_CREDENTIALS           = {GOOGLE_CREDENTIALS} (existe: {os.path.exists(GOOGLE_CREDENTIALS)})")
    print(f"[DEBUG] GOOGLE_CREDENTIALS_ALUMNOS   = {GOOGLE_CREDENTIALS_ALUMNOS} (existe: {os.path.exists(GOOGLE_CREDENTIALS_ALUMNOS)})")
    print(f"[DEBUG] ARCHIVOS_DIR                 = {ARCHIVOS_DIR}")
    print(f"[DEBUG] FOTO_PERFIL_ESTUDIANTE_DIR   = {FOTO_PERFIL_ESTUDIANTE_DIR}")
    print(f"[DEBUG] FOTO_ESTUDIANTE_DIR          = {FOTO_ESTUDIANTE_DIR}")
