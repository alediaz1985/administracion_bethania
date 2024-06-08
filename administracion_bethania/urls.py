from django.contrib import admin
from django.urls import path, include
from apps.administracion_alumnos.views import home_view
from administracion_bethania import views  # Importa las vistas

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('autenticacion/', include('apps.autenticacion.urls')),
    path('cuotas/', include('apps.cuotas.urls')),
    path('docentes/', include('apps.administracion_docentes.urls')),
    path('alumnos/', include('apps.administracion_alumnos.urls')),
    path('niveles/', include('apps.niveles.urls')),  # Asegúrate de incluir esta línea
    path('trigger-error/', views.trigger_error),
]

# Manejadores de errores
handler404 = 'administracion_bethania.views.error_404'
handler500 = 'administracion_bethania.views.error_500'
