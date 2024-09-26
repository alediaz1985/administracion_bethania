# apps/documentos/urls.py
from django.urls import path
from . import views 
from .views import descargar_archivos_nube, vaciar_carpeta_drive,forbidden_view

urlpatterns = [
    path('consulta/', views.consulta_view, name='consulta'),
    
    path('descargar-archivos-nube/', descargar_archivos_nube, name='descargar_archivos_nube'),
    path('subir_comprobante/', views.subir_comprobante_view, name='subir_comprobante'),
    path('vaciar-carpeta-drive/', views.vaciar_carpeta_drive, name='vaciar_carpeta_drive'),
    
    
]
