# apps/comprobantes/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import localtime
from django.template.defaultfilters import filesizeformat  # ✅ en lugar de naturalsize

from .models import Documento

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "drive_file_id",
        "original_filename",
        "estudiante",
        "cuil_estudiante",
        "responsable",
        "cuil_responsable",
        "correo",
        "estado",
        "tamano_humano",   # 👉 usa filesizeformat
        "creado_en",
        "ver_drive",
        "ver_archivo",
    )
    list_select_related = ("estudiante", "responsable")
    search_fields = (
        "drive_file_id",
        "original_filename",
        "correo",
        "cuil_estudiante",
        "cuil_responsable",
        "estudiante__cuil_estudiante",
        "responsable__cuil",
        "estudiante__pk",
        "responsable__pk",
    )
    list_filter = ("estado", "drive_mime_type")
    readonly_fields = (
        "drive_file_id",
        "drive_folder_id",
        "drive_mime_type",
        "drive_web_view_link",
        "original_filename",
        "tamano_bytes",
        "sha256",
        "fecha_subida",
        "procesado_en",
        "estado",
        "error_msg",
        "estudiante",
        "responsable",
        "cuil_estudiante",
        "cuil_responsable",
        "correo",
        "timestamp_form",
        "archivo",
    )
    ordering = ("-fecha_subida",)

    def creado_en(self, obj):
        return localtime(obj.fecha_subida).strftime("%d/%m/%Y %H:%M") if obj.fecha_subida else "—"
    creado_en.short_description = "Creado"

    def tamano_humano(self, obj):
        # si ya guardaste tamano_bytes en el modelo:
        if obj.tamano_bytes:
            return filesizeformat(obj.tamano_bytes)
        # fallback: si por algún motivo no está seteado, intenta desde el archivo
        if obj.archivo and hasattr(obj.archivo, "size"):
            return filesizeformat(obj.archivo.size)
        return "—"
    tamano_humano.short_description = "Tamaño"

    def ver_drive(self, obj):
        return format_html('<a href="{}" target="_blank">Abrir</a>', obj.drive_web_view_link) if obj.drive_web_view_link else "—"
    ver_drive.short_description = "Drive"

    def ver_archivo(self, obj):
        return format_html('<a href="{}" download>Descargar</a>', obj.archivo.url) if obj.archivo else "—"
    ver_archivo.short_description = "Archivo"

# ==========================================================
# 🧾 ADMIN — COMPROBANTE DE PAGO
# ==========================================================
from .models import ComprobantePago

@admin.register(ComprobantePago)
class ComprobantePagoAdmin(admin.ModelAdmin):
    list_display = (
        'marca_temporal',
        'cuil_estudiante',
        'cuil_responsable',
        'correo',
        'estado',
        'estudiante',
    )
    list_filter = ('estado',)
    search_fields = ('cuil_estudiante', 'cuil_responsable', 'correo')
    ordering = ('-marca_temporal',)
