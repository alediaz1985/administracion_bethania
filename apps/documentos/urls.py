from django.urls import path
from . import views 
#from .views import descargar_archivos_nube, vaciar_carpeta_drive, forbidden_view

urlpatterns = [
    path('consulta/', views.consulta_view, name='consulta'),
    
    #path('descargar-archivos-nube/', descargar_archivos_nube, name='descargar_archivos_nube'),
    #path('subir_comprobante/', views.subir_comprobante_view, name='subir_comprobante'),
    #path('vaciar-carpeta-drive/', views.vaciar_carpeta_drive, name='vaciar_carpeta_drive'),
    #path('forbidden/', forbidden_view, name='forbidden_view'),
    path('list-files/', views.list_files, name='lista_de_archivos'),  # Ruta ajustada
    path('consulta_comprobantes/', views.consulta_comprobantes, name='consulta_comprobantes'),
    path('descargar-archivos-nube/', views.descargar_archivos_nube, name='descargar_archivos_nube'),
    path('vaciar-carpeta-drive/', views.vaciar_carpeta_drive, name='vaciar_carpeta_drive'),
    path('subir_comprobante/', views.subir_comprobante, name='subir_comprobante'),
    path('exito-descarga/', views.exito_descarga, name='exito_descarga'),
]
