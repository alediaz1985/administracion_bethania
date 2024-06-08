from django.urls import path
from . import views

urlpatterns = [
    path('', views.docente_list, name='docente_list'),
    path('consultar/', views.consultar_docente, name='consultar_docente'),
    path('registrar/', views.registrar_docente, name='registrar_docente'),
]
