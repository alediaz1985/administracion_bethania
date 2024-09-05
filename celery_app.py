from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Establece el entorno de Django para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'administracion_bethania.settings')

app = Celery('administracion_bethania')

# Usar un string aquí significa que el worker no tendrá que serializar
# la configuración del objeto en tiempo de ejecución.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carga tareas de todos los módulos de tareas registradas en Django.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
