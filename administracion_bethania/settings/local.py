# administracion_bethania/settings/local.py
from .base import *

DEBUG = env_bool('DEBUG', True)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
