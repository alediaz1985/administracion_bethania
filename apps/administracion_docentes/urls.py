from django.urls import path
from . import views

urlpatterns = [
    path('docentes/registrar/', views.registrar_docente, name='registrar_docente'),
    path('docentes/', views.listar_docentes, name='listar_docentes'),
    path('docentes/consultar/', views.consultar_docente, name='consultar_docente'),
    path('docentes/editar/<str:cuil>/', views.editar_docente, name='editar_docente'),
    path('docentes/eliminar/<str:cuil>/', views.eliminar_docente, name='eliminar_docente'),
]
