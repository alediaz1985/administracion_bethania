from django.urls import path
from . import views

app_name = "comprobantes"  # 👈 importante

urlpatterns = [
    path('', views.home_comprobantes, name='home'),
    path('consulta/', views.consulta_view, name='consulta'),
    path('list-files/', views.list_files, name='list_files'),  # 👈 nombre alineado
    path('consulta_comprobantes/', views.consulta_comprobantes, name='consulta_comprobantes'),
    path('descargar-archivos-nube/', views.descargar_archivos_nube, name='descargar_archivos_nube'),
    path('vaciar-carpeta-drive/', views.vaciar_carpeta_drive, name='vaciar_carpeta_drive'),
    path('subir_comprobante/', views.subir_comprobante, name='subir_comprobante'),
    path('exito-descarga/', views.exito_descarga, name='exito_descarga'),
]
