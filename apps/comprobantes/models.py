# apps/comprobantes/models.py
from django.db import models
from apps.administracion_alumnos.models import Estudiante, Responsable

def ruta_comprobantes(instance, filename):
    return f"documentos/comprobantes/{instance.drive_file_id}"

class Documento(models.Model):
    correo = models.EmailField(max_length=150, verbose_name="Correo remitente (Form)")
    timestamp_form = models.DateTimeField(null=True, blank=True, verbose_name="Fecha/hora del formulario")

    drive_file_id = models.CharField(max_length=64, unique=True, verbose_name="ID Drive")
    drive_folder_id = models.CharField(max_length=128, blank=True, default="", verbose_name="Carpeta Drive")
    drive_mime_type = models.CharField(max_length=150, blank=True, default="", verbose_name="MIME")
    drive_web_view_link = models.URLField(blank=True, default="", verbose_name="Link web")
    original_filename = models.CharField(max_length=255, blank=True, default="", verbose_name="Nombre original")

    archivo = models.FileField(upload_to=ruta_comprobantes, verbose_name="Archivo (local)")

    estudiante = models.ForeignKey(Estudiante, on_delete=models.PROTECT, related_name="comprobantes")
    cuil_estudiante = models.CharField(max_length=11, db_index=True)

    responsable = models.ForeignKey(Responsable, on_delete=models.PROTECT, related_name="comprobantes")
    cuil_responsable = models.CharField(max_length=11, db_index=True)

    tamano_bytes = models.BigIntegerField(null=True, blank=True)
    sha256 = models.CharField(max_length=64, blank=True, default="")

    fecha_subida = models.DateTimeField(auto_now_add=True)
    procesado_en = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[("ok", "OK"), ("omitido", "Omitido"), ("error", "Error")],
        default="ok",
    )
    error_msg = models.TextField(blank=True, default="")

    class Meta:
        db_table = "documento_comprobante"
        ordering = ["-fecha_subida"]

    def __str__(self):
        return f"Comprobante {self.drive_file_id} - {self.estudiante}"
