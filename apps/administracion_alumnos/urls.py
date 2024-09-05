from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.alumno_list, name='alumno_list'),
    path('detail/<int:pk>/', views.alumno_detail, name='alumno_detail'),
    path('edit/<int:pk>/', views.alumno_edit, name='alumno_edit'),
    path('delete/<int:pk>/', views.alumno_delete, name='alumno_delete'),
    path('consultar/', views.consultar_alumno, name='consultar_alumno'),
    path('ver-datos-alumno/<int:pk>/', views.ver_datos_alumno, name='ver_datos_alumno'),
    path('ver-datos-alumno/<int:alumno_id>/', views.ver_datos_alumno, name='ver_datos_alumno'),
    path('generar_pdf_alumno/<int:alumno_id>/', views.generar_pdf_alumno_view, name='generar_pdf_alumno'),
    path('generar_pdf_lista_alumnos/', views.generar_pdf_lista_alumnos_view, name='generar_pdf_lista_alumnos'),
    path('registrar_alumno/', views.registrar_alumno, name='registrar_alumno'),
]