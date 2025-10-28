from django.db import models
from django.utils import timezone
from datetime import date
from decimal import Decimal
from django.core.exceptions import ValidationError

# ============================================================
# 🗓️ CICLO LECTIVO (Un registro por año)
# ============================================================
class CicloLectivo(models.Model):
    anio = models.PositiveIntegerField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'adm_ciclo_lectivo'
        ordering = ['-anio']

    def __str__(self):
        return str(self.anio)


# ============================================================
# 🏫 NIVELES Y SUBNIVELES (Estructura fija)
# ============================================================
class Nivel(models.Model):
    nombre = models.CharField(max_length=50, unique=True)  # Inicial, Primario, Secundario

    class Meta:
        db_table = 'adm_nivel'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Subnivel(models.Model):
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE, related_name='subniveles')
    nombre = models.CharField(max_length=50)  # Ej: Sala de 5 años, 3° Grado, 5° Año

    class Meta:
        db_table = 'adm_subnivel'
        unique_together = ('nivel', 'nombre')
        ordering = ['nivel__nombre', 'nombre']

    def __str__(self):
        return f"{self.nivel.nombre} - {self.nombre}"


# ============================================================
# 💰 MONTOS POR NIVEL (con vigencia y aumentos)
# ============================================================
class MontoNivel(models.Model):
    ciclo = models.ForeignKey(CicloLectivo, on_delete=models.CASCADE, related_name='montos_nivel')
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE, related_name='montos_nivel')

    monto_inscripcion = models.DecimalField(max_digits=10, decimal_places=2)
    monto_cuota = models.DecimalField(max_digits=10, decimal_places=2)

    # Fechas de vigencia (para reflejar aumentos)
    fecha_vigencia_desde = models.DateField(default=timezone.now)
    fecha_vigencia_hasta = models.DateField(blank=True, null=True)

    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'adm_monto_nivel'
        ordering = ['nivel', 'fecha_vigencia_desde']

    def __str__(self):
        return f"{self.ciclo.anio} - {self.nivel.nombre} (${self.monto_cuota})"


# ============================================================
# 🎓 BECA / BENEFICIO
# ============================================================
class Beca(models.Model):
    TIPO_CHOICES = [
        ('Porcentaje', 'Porcentaje'),
        ('Monto fijo', 'Monto fijo'),
    ]

    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'adm_beca'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.tipo}: {self.valor})"


# ============================================================
# 🧾 INSCRIPCIÓN ADMINISTRATIVA (Alumno inscrito al ciclo)
# ============================================================
class InscripcionAdministrativa(models.Model):
    from apps.administracion_alumnos.models import Estudiante  # Import diferido para evitar bucle

    TURNO_CHOICES = [
        ('Mañana', 'Mañana'),
        ('Tarde', 'Tarde'),
    ]

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='inscripciones_admin')
    ciclo = models.ForeignKey(CicloLectivo, on_delete=models.CASCADE, related_name='inscripciones')
    nivel = models.ForeignKey(Nivel, on_delete=models.PROTECT)
    subnivel = models.ForeignKey(Subnivel, on_delete=models.PROTECT)
    turno = models.CharField(max_length=20, choices=TURNO_CHOICES)

    fecha_inscripcion = models.DateField(auto_now_add=True)
    monto_inscripcion = models.DecimalField(max_digits=10, decimal_places=2)

    beca = models.ForeignKey(Beca, on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'adm_inscripcion_administrativa'
        ordering = ['-ciclo__anio', 'nivel', 'subnivel']

    def __str__(self):
        return f"{self.estudiante} - {self.ciclo.anio} ({self.nivel.nombre})"


# ============================================================
# 📆 CUOTAS (10 por ciclo: Marzo–Diciembre)
# ============================================================
class Cuota(models.Model):
    inscripcion = models.ForeignKey(InscripcionAdministrativa, on_delete=models.CASCADE, related_name='cuotas')
    mes = models.PositiveIntegerField()  # 3 a 12 (marzo–diciembre)
    anio = models.PositiveIntegerField()

    monto_original = models.DecimalField(max_digits=10, decimal_places=2)
    monto_descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_interes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_final = models.DecimalField(max_digits=10, decimal_places=2)

    fecha_vencimiento = models.DateField()  # Día 16 de cada mes
    fecha_pago = models.DateField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('Pendiente', 'Pendiente'),
            ('Pagada', 'Pagada'),
            ('Vencida', 'Vencida'),
        ],
        default='Pendiente'
    )

    class Meta:
        db_table = 'adm_cuota'
        ordering = ['anio', 'mes']

    def __str__(self):
        return f"{self.inscripcion.estudiante} - {self.mes}/{self.anio} (${self.monto_final})"
    
    def aplicar_interes(self):
        """
        Si la cuota está pendiente y venció (día actual > fecha_vencimiento),
        aplica un recargo del 10% y cambia su estado a 'Vencida'.
        """
        hoy = date.today()
        if self.estado == 'Pendiente' and hoy > self.fecha_vencimiento:
            dias_vencida = (hoy - self.fecha_vencimiento).days
            if dias_vencida > 0:
                interes = Decimal(self.monto_final) * Decimal('0.10')  # +10%
                self.monto_interes = interes
                self.monto_final = Decimal(self.monto_original) - Decimal(self.monto_descuento) + interes
                self.estado = 'Vencida'
                self.save()


# ============================================================
# 💳 PAGOS (opcional: si querés registrar recibos o medios)
# ============================================================
class Pago(models.Model):
    METODO_CHOICES = [
        ('Efectivo', 'Efectivo'),
        ('Transferencia', 'Transferencia'),
        ('Tarjeta', 'Tarjeta'),
        ('Otro', 'Otro'),
    ]

    fecha_pago = models.DateTimeField(default=timezone.now)
    metodo_pago = models.CharField(max_length=30, choices=METODO_CHOICES)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    cuotas_pagadas = models.ManyToManyField(Cuota, related_name='pagos')

    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'adm_pago'
        ordering = ['-fecha_pago']

    def __str__(self):
        return f"Pago {self.id} - ${self.monto_total} ({self.metodo_pago})"
