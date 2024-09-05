from django.urls import path
from . import views

urlpatterns = [
    path('consultar/', views.consultar_docente, name='consultar_docente'),
    path('ver/<str:cuil>/', views.ver_datos_docente, name='ver_datos_docente'),
    path('eliminar/<str:cuil>/', views.eliminar_docente, name='eliminar_docente'),
    path('editar/<str:cuil>/', views.editar_docente, name='editar_docente'),
    path('listar/', views.listar_docentes, name='listar_docentes'),
    path('registrar/', views.registrar_docente, name='registrar_docente'),
]
