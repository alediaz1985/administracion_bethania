# administracion_bethania/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "administracion_bethania.settings.production"  # en server, mejor production
)
application = get_wsgi_application()
