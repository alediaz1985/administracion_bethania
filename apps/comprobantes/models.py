from django.db import models
from apps.administracion_alumnos.models import Estudiante, Responsable

def ruta_comprobantes(instance, filename):
    """
    Guarda los archivos en /media/documentos/comprobantes/
    """
    return f"documentos/comprobantes/{filename}"

class Documento(models.Model):
    # Obligatorio (se setea en la vista desde settings.INSTITUCION_EMAIL)
    correo = models.EmailField(max_length=150, verbose_name="Correo institucional")

    # Archivo y nombre
    archivo = models.FileField(upload_to=ruta_comprobantes, verbose_name="Comprobante adjunto")
    nombre = models.CharField(max_length=255, verbose_name="Nombre del comprobante")

    # Relaciones y CUILs (obligatorios)
    estudiante = models.ForeignKey(
        Estudiante, on_delete=models.CASCADE, related_name="comprobantes", verbose_name="Estudiante"
    )
    cuil_estudiante = models.CharField(max_length=11, verbose_name="CUIL del estudiante")

    responsable = models.ForeignKey(
        Responsable, on_delete=models.CASCADE, related_name="comprobantes", verbose_name="Responsable de pago"
    )
    cuil_responsable = models.CharField(max_length=11, verbose_name="CUIL del responsable")

    # Meta
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comprobante de {self.estudiante} ({self.fecha_subida:%d/%m/%Y})"

    class Meta:
        db_table = "documento_comprobante"
        ordering = ["-fecha_subida"]
        verbose_name = "Comprobante"
        verbose_name_plural = "Comprobantes"
