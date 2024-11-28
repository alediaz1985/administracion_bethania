import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-k&i2xs2b#vq!smy1jzvgi^ueoz-v8_d6exdhmd%)*r_*&_mt=q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Application definition

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
    'apps.cuotas',
    'apps.administracion_docentes',
    'apps.administracion_alumnos',
    'apps.niveles',
    'apps.documentos',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'administracion_bethania.middleware.LoginRequiredMiddleware',  # Middleware personalizado
]

ROOT_URLCONF = 'administracion_bethania.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bethania2024',
        'USER': 'admin_remoto',
        'PASSWORD': 'admin123_remoto',
        'HOST': '190.137.235.91',
        'PORT': '3307',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'es-ar'

TIME_ZONE = 'America/Argentina/Buenos_Aires'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Configuración para encontrar archivos estáticos en las aplicaciones
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Configuración de archivos de medios
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# URL de inicio de sesión
LOGIN_URL = 'iniciar_sesion'



GOOGLE_CREDENTIALS = os.path.join(BASE_DIR, 'credentials.json')

#DRIVE_FOLDER_ID = '1lyxImVDTJt9Q2P9QDm0M_wHz9jgodfGp'
# Configura la ruta a tu archivo de credenciales
#GOOGLE_CREDENTIALS = os.path.join(BASE_DIR, 'administracion_bethania', 'credentials.json')
# Configura la ID de la carpeta de Google Drive
DRIVE_FOLDER_ID = '1lyxImVDTJt9Q2P9QDm0M_wHz9jgodfGp'  # Este es el ID de la carpeta de Google Drive

# Directorio de archivos locales
ARCHIVOS_DIR = os.path.join(BASE_DIR, 'media', 'documentos')

CRISPY_TEMPLATE_PACK = 'bootstrap4'