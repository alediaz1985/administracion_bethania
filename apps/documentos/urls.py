# apps/documentos/urls.py
from django.urls import path
from . import views1
from .views1 import descargar_archivos_nube

urlpatterns = [
    path('consulta/', views1.consulta_view, name='consulta'),
    path('descargar-archivos-nube/', descargar_archivos_nube, name='descargar_archivos_nube'),
    path('subir_comprobante/', views1.subir_comprobante_view, name='subir_comprobante'),
]
