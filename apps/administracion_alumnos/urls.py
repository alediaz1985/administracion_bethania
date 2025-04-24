from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('list/', views.estudiante_list, name='estudiante_list'),
    path('detail/<int:pk>/', views.estudiante_detail, name='estudiante_detail'),
    path('edit/<int:pk>/', views.estudiante_edit,name='estudiante_edit'),
    path('delete/<int:pk>/', views.estudiante_delete, name='estudiante_delete'),
    path('consultar/', views.estudiante_consultar, name='consultar_alumno'),
    #path('ver-datos/<int:pk>/', views.ver_datos_estudiante, name='ver_datos_estudiante'),
    path('ver-datos-estudiante/<int:pk>/', views.ver_datos_estudiante, name='ver_datos_estudiante'),
    #path('ver-datos-estudiante/<int:estudiante_id>/', views.ver_datos_estudiante, name='ver_datos_estudiante'),
    path('generar_pdf_estudiante/<int:estudiante_id>/', views.generar_pdf_estudiante_view, name='generar_pdf_estudiante'),
    path('generar_pdf_lista_estudiantes/', views.generar_pdf_lista_estudiantes_view, name='generar_pdf_lista_alumnos'),
    path('registrar_estudiante/', views.registrar_estudiante, name='registrar_alumno'),
    path('generar-contrato/<int:estudiante_id>/', views.generar_contrato_view, name='generar_contrato'),
    path('descargar_archivos/', views.descargar_todos_archivos, name='descargar_archivos_alumnos'),
    path('lista-fotos-estudiantes/', views.lista_fotos_estudiantes, name='lista_fotos_estudiantes'),
    path('confirmar_aprobacion/<int:estudiante_id>/', views.confirmar_aprobacion, name='confirmar_aprobacion'),
]

# Configuración para servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)