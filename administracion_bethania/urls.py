# administracion_bethania/urls.py
from django.contrib import admin
from django.urls import path, include
from apps.administracion.views import home
from administracion_bethania import views  # Importa las vistas

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('autenticacion/', include('apps.autenticacion.urls')),
    path('alumnos/', include('apps.administracion_alumnos.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('administracion/', include(('apps.administracion.urls', 'administracion'), namespace='administracion')),
    # path('documentos/', include('apps.documentos.urls')),
    # path('trigger-error/', views.trigger_error),
    # path('forbidden/', views.forbidden_view, name='forbidden'),  # Ruta para la vista de acceso denegado
]

# Manejadores de errores
handler404 = 'administracion_bethania.views.error_404'
handler500 = 'administracion_bethania.views.error_500'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


