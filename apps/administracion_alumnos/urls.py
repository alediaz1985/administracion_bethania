from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.estudiante_list, name='estudiante_list'),
    path('detail/<int:pk>/', views.estudiante_detail, name='estudiante_detail'),
    path('edit/<int:pk>/', views.estudiante_edit, name='estudiante_edit'),
    path('delete/<int:pk>/', views.estudiante_delete, name='estudiante_delete'),
    path('consultar/', views.estudiante_consultar, name='consultar_alumno'),
    #path('ver-datos/<int:pk>/', views.ver_datos_estudiante, name='ver_datos_estudiante'),
    path('ver-datos-estudiante/<int:pk>/', views.ver_datos_estudiante, name='ver_datos_estudiante'),
    #path('ver-datos-estudiante/<int:estudiante_id>/', views.ver_datos_estudiante, name='ver_datos_estudiante'),
    path('generar_pdf_estudiante/<int:estudiante_id>/', views.generar_pdf_estudiante_view, name='generar_pdf_estudiante'),
    path('generar_pdf_lista_estudiantes/', views.generar_pdf_lista_estudiantes_view, name='generar_pdf_lista_alumnos'),
    path('registrar_estudiante/', views.registrar_estudiante, name='registrar_alumno'),
    path('generar-contrato/<int:estudiante_id>/', views.generar_contrato_view, name='generar_contrato'),
]
