# apps/comprobantes/models.py
from django.db import models
from apps.administracion_alumnos.models import Estudiante, Responsable
from datetime import datetime

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

# ==========================================================
# 🧾 NUEVO MODELO — COMPROBANTE DE PAGO
# ==========================================================

class ComprobantePago(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente de revisión'),
        ('Procesado', 'Procesado'),
    ]

    # 🕒 Datos principales
    marca_temporal = models.CharField(max_length=100)
    correo = models.EmailField()
    url_comprobante = models.URLField(max_length=500)

    # 👥 Identificación
    cuil_estudiante = models.CharField(max_length=20)
    cuil_responsable = models.CharField(max_length=20, blank=True, null=True)

    # 🔗 Relación con estudiante (automática si el CUIL coincide)
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comprobantes_pago'
    )

    # ⚙️ Estado del comprobante
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')

    # 🗓️ Fecha en que se registró (texto)
    fecha_registro = models.CharField(max_length=100)

    class Meta:
        db_table = 'adm_comprobantes_pago'
        ordering = ['-marca_temporal']
        verbose_name = "Comprobante de Pago"
        verbose_name_plural = "Comprobantes de Pago"

    def save(self, *args, **kwargs):
        if self.marca_temporal:
            # Si viene con microsegundos, los eliminamos
            try:
                dt = datetime.fromisoformat(str(self.marca_temporal))
                self.marca_temporal = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass  # deja como está si no lo puede convertir
        # Relación con estudiante
        if self.cuil_estudiante and not self.estudiante:
            estudiante = Estudiante.objects.filter(cuil_estudiante=self.cuil_estudiante).first()
            if estudiante:
                self.estudiante = estudiante
        super().save(*args, **kwargs)

    def __str__(self):
        fecha = self.marca_temporal or "Sin fecha"
        return f"Comprobante — {self.cuil_estudiante} ({fecha})"
