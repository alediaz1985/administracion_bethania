from django.urls import path
from . import views

# apps/comprobantes/urls.py
from django.urls import path
from .views_import_sheet import importar_comprobantes_desde_sheet_auth
from .views import descargar_archivos_nube  # tu vista actual por carpeta


app_name = "comprobantes"  # 👈 importante para los {% url 'comprobantes:...' %} del template

urlpatterns = [
    # --- Panel principal ---
    path("", views.home_comprobantes, name="home"),

    # --- Consultas ---
    path("consulta/", views.consulta_view, name="consulta"),  # búsqueda local (con o sin AJAX)
    path("consulta_comprobantes/", views.consulta_comprobantes, name="consulta_comprobantes"),

    # --- Google Drive ---
    path("list-files/", views.list_files, name="list_files"),  # listar archivos de Drive
    path("descargar-archivos-nube/", views.descargar_archivos_nube, name="descargar_archivos_nube"),
    path("vaciar-carpeta-drive/", views.vaciar_carpeta_drive, name="vaciar_carpeta_drive"),

    # --- Subida manual ---
    path("subir_comprobante/", views.subir_comprobante, name="subir_comprobante"),

    # --- Compatibilidad / feedback ---
    path("exito-descarga/", views.exito_descarga, name="exito_descarga"),

    path("descargar_nube/", descargar_archivos_nube, name="descargar_nube"),
    path('descargar/', views.descargar_archivos_nube, name='descargar_archivos_nube'),
    path("importar_sheet_auth/", importar_comprobantes_desde_sheet_auth, name="importar_sheet_auth"),

    # --- comprobantes ---
    path("administrar/", views.lista_comprobantes, name="lista_comprobantes"),
    path('cambiar-estado/', views.cambiar_estado_comprobante, name='cambiar_estado_comprobante'),
]
