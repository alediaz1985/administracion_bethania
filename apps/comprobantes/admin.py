from django.contrib import admin
from .models import Documento

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha_subida", "estudiante", "responsable", "correo", "nombre")
    search_fields = (
        "nombre", "correo", "cuil_estudiante", "cuil_responsable",
        "estudiante__apellidos_estudiante", "estudiante__nombres_estudiante",
        "responsable__apellidos", "responsable__nombres",
    )
    list_filter = ("fecha_subida",)
