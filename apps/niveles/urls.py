from django.urls import path
from . import views

urlpatterns = [
    path('', views.niveles_list, name='niveles_list'),
    path('registrar/', views.registrar_nivel, name='registrar_nivel'),
    path('editar/', views.editar_nivel, name='editar_nivel'),
]
