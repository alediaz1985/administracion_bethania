# administracion_bethania/urls.py
from django.contrib import admin
from django.urls import path, include
from apps.administracion.views import home
from administracion_bethania import views  # Importa las vistas globales (errores y pruebas)

from django.conf import settings
from django.conf.urls.static import static


# ======================================================
# RUTAS PRINCIPALES DEL SISTEMA
# ======================================================

urlpatterns = [
    path('admin/', admin.site.urls),

    # Página principal
    path('', home, name='home'),

    # Apps principales
    path('autenticacion/', include('apps.autenticacion.urls')),
    path('alumnos/', include('apps.administracion_alumnos.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path(
        'administracion/',
        include(('apps.administracion.urls', 'administracion'), namespace='administracion')
    ),
    path(
        'documentos/',
        include(('apps.documentos.urls', 'documentos'), namespace='documentos')
    ),
]


# ======================================================
# RUTAS DE PRUEBA PARA PAGINAS DE ERROR
# ======================================================

urlpatterns += [
    path('test-errors/', views.test_errors_menu, name='test_errors_menu'),  # menú de pruebas
    path('force-400/', views.force_400, name='force_400'),                  # fuerza 400
    path('force-403/', views.force_403, name='force_403'),                  # fuerza 403
    # 404: probalo yendo a /no-existe (no hace falta ruta)
    path('force-500/', views.force_500, name='force_500'),                  # fuerza 500
    # opcional: si querés también podés probar trigger-error
    # path('trigger-error/', views.trigger_error),
]


# ======================================================
# MANEJADORES DE ERRORES HTTP GLOBALES
# ======================================================

handler404 = 'administracion_bethania.views.error_404_view'
handler500 = 'administracion_bethania.views.error_500_view'
handler403 = 'administracion_bethania.views.forbidden_view'
handler400 = 'administracion_bethania.views.error_400_view'


# ======================================================
# ARCHIVOS ESTÁTICOS Y MEDIA (solo en desarrollo)
# ======================================================

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



# Habilitar rutas del Debug Toolbar si está instalado
if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns