# apps/documentos/urls.py
from django.urls import path
from . import views1

urlpatterns = [
    path('consulta/', views1.consulta_view, name='consulta'),
    path('subir_comprobante/', views1.subir_comprobante_view, name='subir_comprobante'),
]
