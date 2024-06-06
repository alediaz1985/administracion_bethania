from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('autenticacion/', include('apps.autenticacion.urls')),
    path('cuotas/', include('apps.cuotas.urls')),
    path('docentes/', include('apps.administracion_docentes.urls')),
    path('alumnos/', include('apps.administracion_alumnos.urls')),
]