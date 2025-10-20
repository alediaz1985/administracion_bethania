from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from apps.administracion_alumnos.models import Estudiante


# ==========================
# Utilidades monetarias
# ==========================
def money(val) -> Decimal:
    if val is None:
        val = Decimal("0")
    if not isinstance(val, Decimal):
        val = Decimal(str(val))
    return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ==========================
# Catálogos / Estructura Académica
# ==========================
from django.db import models

class CicloLectivo(models.Model):
    anio = models.PositiveIntegerField(verbose_name="Año Lectivo", unique=True)
    fecha_inicio = models.DateField(verbose_name="Inicio")
    fecha_fin = models.DateField(verbose_name="Fin")
    activo = models.BooleanField(default=False)  # <— FALTA EN TU MODELO

    class Meta:
        db_table = "ciclos_lectivos"
        verbose_name = "Ciclo lectivo"
        verbose_name_plural = "Ciclos lectivos"
        ordering = ["-anio"]

    def __str__(self):
        return f"Ciclo {self.anio}"

    def save(self, *args, **kwargs):
        # Si este ciclo se marca activo, desactiva los demás
        if self.activo:
            CicloLectivo.objects.exclude(pk=self.pk).update(activo=False)
        super().save(*args, **kwargs)


class Nivel(models.Model):
    """
    Ej.: Inicial, Primario, Secundario.
    """
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "niveles"
        verbose_name = "Nivel"
        verbose_name_plural = "Niveles"
        ordering = ["id"]

    def __str__(self):
        return self.nombre


class Curso(models.Model):
    """
    Subnivel/curso dentro de un nivel.
    Ej.: Sala 3, Sala 4, Sala 5 (Inicial) | 1° a 7° (Primario) | 1° a 5° (Secundario)
    """
    nivel = models.ForeignKey(Nivel, on_delete=models.PROTECT, related_name="cursos")
    nombre = models.CharField(max_length=100)
    # Si None ⇒ usa tarifa del nivel; si se setea ⇒ override por curso
    monto_cuota_override = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Monto mensual (override)"
    )
    monto_inscripcion_override = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Inscripción (override)"
    )

    class Meta:
        db_table = "cursos"
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        unique_together = [("nivel", "nombre")]
        ordering = ["nivel__nombre", "id"]

    def __str__(self):
        return f"{self.nivel} - {self.nombre}"


class TarifaNivel(models.Model):
    """
    Monto base por NIVEL y CICLO (todos los cursos de ese nivel heredan estos montos).
    """
    ciclo = models.ForeignKey(CicloLectivo, on_delete=models.CASCADE, related_name="tarifas_nivel")
    nivel = models.ForeignKey(Nivel, on_delete=models.PROTECT, related_name="tarifas")
    monto_inscripcion = models.DecimalField(max_digits=10, decimal_places=2)
    monto_cuota_mensual = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "tarifas_nivel"
        verbose_name = "Tarifa por nivel"
        verbose_name_plural = "Tarifas por nivel"
        unique_together = [("ciclo", "nivel")]
        indexes = [models.Index(fields=["ciclo", "nivel"])]

    def __str__(self):
        return f"{self.ciclo} - {self.nivel}"


# ==========================
# Reglas de vencimiento y recargos
# ==========================
class VencimientoMensual(models.Model):
    """
    Define, por ciclo y mes (1..12), el último día de pago sin recargo y el % de recargo posterior.
    Ej.: mes=3 (marzo), dia_ultimo_sin_recargo=10, recargo_porcentaje=10.00
    """
    ciclo = models.ForeignKey(CicloLectivo, on_delete=models.CASCADE, related_name="vencimientos")
    mes = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    dia_ultimo_sin_recargo = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text="Día máximo para pagar sin recargo"
    )
    recargo_porcentaje = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("10.00"),
        help_text="Porcentaje a aplicar fuera de término"
    )

    class Meta:
        db_table = "vencimientos_mensuales"
        verbose_name = "Vencimiento mensual"
        verbose_name_plural = "Vencimientos mensuales"
        unique_together = [("ciclo", "mes")]
        ordering = ["ciclo__anio", "mes"]

    def __str__(self):
        return f"{self.ciclo} - Mes {self.mes} (hasta el {self.dia_ultimo_sin_recargo} sin recargo)"


# ==========================
# Beneficios / Descuentos
# ==========================
class Beneficio(models.Model):
    class Tipo(models.TextChoices):
        BECA = "BECA", _("Beca")
        HERMANOS = "HERMANOS", _("Descuento por hermanos")
        MANUAL = "MANUAL", _("Descuento manual")

    nombre = models.CharField(max_length=120)
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.MANUAL)
    # porcentaje (ej 20.00) y/o monto fijo; se suman (primero fijo, luego porcentaje) o aplican como corresponda
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    monto_fijo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prioridad = models.PositiveSmallIntegerField(default=100, help_text="Menor número ⇒ se aplica primero")
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "beneficios"
        verbose_name = "Beneficio/Descuento"
        verbose_name_plural = "Beneficios/Descuentos"
        ordering = ["prioridad", "id"]

    def __str__(self):
        etiqueta = self.nombre
        if self.porcentaje:
            etiqueta += f" (-{self.porcentaje}% )"
        if self.monto_fijo:
            etiqueta += f" (-${self.monto_fijo})"
        return etiqueta


class BeneficioInscripcion(models.Model):
    """
    Asigna beneficios a una inscripción (estudiante+ciclo). Permite múltiples combinaciones.
    """
    inscripcion = models.ForeignKey("Inscripcion", on_delete=models.CASCADE, related_name="beneficios")
    beneficio = models.ForeignKey(Beneficio, on_delete=models.PROTECT)
    desde = models.DateField(null=True, blank=True)
    hasta = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "beneficios_inscripcion"
        verbose_name = "Beneficio de inscripción"
        verbose_name_plural = "Beneficios de inscripción"
        unique_together = [("inscripcion", "beneficio")]
        indexes = [models.Index(fields=["inscripcion", "activo"])]

    def __str__(self):
        return f"{self.inscripcion} -> {self.beneficio}"


# ==========================
# Inscripción y Cuotas
# ==========================
class Inscripcion(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.PROTECT, related_name="inscripciones")
    ciclo = models.ForeignKey(CicloLectivo, on_delete=models.PROTECT, related_name="inscripciones")
    nivel = models.ForeignKey(Nivel, on_delete=models.PROTECT, related_name="inscripciones")
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT, related_name="inscripciones")
    fecha_inscripcion = models.DateField(auto_now_add=True)
    # Se guarda el monto de inscripción vigente al momento de inscribir (puede recalcularse si querés)
    monto_inscripcion = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "inscripciones"
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"
        unique_together = [("estudiante", "ciclo")]
        indexes = [models.Index(fields=["ciclo", "nivel", "curso"])]

    def __str__(self):
        return f"{self.estudiante} - {self.ciclo} - {self.curso}"

    # Helpers para resolver montos base
    def get_monto_base_cuota(self) -> Decimal:
        # 1) override por curso
        if self.curso.monto_cuota_override is not None:
            return money(self.curso.monto_cuota_override)
        # 2) tarifa por nivel+ciclo
        tarifa = TarifaNivel.objects.get(ciclo=self.ciclo, nivel=self.nivel)
        return money(tarifa.monto_cuota_mensual)

    def get_monto_base_inscripcion(self) -> Decimal:
        if self.curso.monto_inscripcion_override is not None:
            return money(self.curso.monto_inscripcion_override)
        tarifa = TarifaNivel.objects.get(ciclo=self.ciclo, nivel=self.nivel)
        return money(tarifa.monto_inscripcion)


class Cuota(models.Model):
    """
    Generada por inscripción para cada mes del ciclo.
    Guarda el monto base (resuelto en el momento de generar),
    los descuentos y recargos aplicados, y el total final.
    """
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE, related_name="cuotas")
    mes = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    monto_base = models.DecimalField(max_digits=10, decimal_places=2)
    monto_descuentos = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    monto_recargos = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total_a_pagar = models.DecimalField(max_digits=10, decimal_places=2)
    pagada = models.BooleanField(default=False)
    fecha_pago = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "cuotas"
        verbose_name = "Cuota"
        verbose_name_plural = "Cuotas"
        unique_together = [("inscripcion", "mes")]
        indexes = [
            models.Index(fields=["inscripcion", "mes"]),
            models.Index(fields=["pagada"]),
        ]
        ordering = ["inscripcion__ciclo__anio", "inscripcion__curso__nivel__nombre", "mes"]

    def __str__(self):
        return f"{self.inscripcion} - Mes {self.mes}"

    # ==========================
    # Reglas de cálculo
    # ==========================
    def calcular_descuentos(self, fecha_ref: date | None = None) -> Decimal:
        """
        Suma beneficios activos a la fecha_ref.
        Se aplican por prioridad: monto fijo, luego porcentaje.
        """
        today = fecha_ref or date.today()
        total_desc = money(0)
        beneficios = (
            self.inscripcion.beneficios.filter(activo=True)
            .select_related("beneficio")
            .order_by("beneficio__prioridad", "id")
        )
        base = money(self.monto_base)
        tmp_total = base

        for bi in beneficios:
            b = bi.beneficio
            # Ventana temporal
            if bi.desde and today < bi.desde:
                continue
            if bi.hasta and today > bi.hasta:
                continue
            # Monto fijo
            if b.monto_fijo:
                restar = money(b.monto_fijo)
                tmp_total = money(max(Decimal("0.00"), tmp_total - restar))
            # Porcentaje
            if b.porcentaje:
                restar = (tmp_total * money(b.porcentaje) / Decimal("100")).quantize(Decimal("0.01"))
                tmp_total = money(max(Decimal("0.00"), tmp_total - restar))

        total_desc = money(base - tmp_total)
        return total_desc

    def calcular_recargo(self, fecha_pago_date: date | None = None) -> Decimal:
        """
        Si se paga después del 'dia_ultimo_sin_recargo' del mes correspondiente al ciclo,
        aplica % de recargo según VencimientoMensual.
        """
        if fecha_pago_date is None:
            return money(0)

        try:
            regla = VencimientoMensual.objects.get(ciclo=self.inscripcion.ciclo, mes=self.mes)
        except VencimientoMensual.DoesNotExist:
            return money(0)

        # Determinar el límite de día sin recargo
        if fecha_pago_date.day <= regla.dia_ultimo_sin_recargo:
            return money(0)

        porcentaje = money(regla.recargo_porcentaje or 0)
        recargo = (money(self.monto_base) * porcentaje / Decimal("100")).quantize(Decimal("0.01"))
        return money(recargo)

    def recalcular(self, fecha_pago_dt: datetime | None = None) -> None:
        """
        Recalcula descuentos/recargos y total.
        No guarda la instancia; sólo actualiza campos en memoria.
        """
        fecha_ref = (fecha_pago_dt.date() if fecha_pago_dt else date.today())
        descuentos = self.calcular_descuentos(fecha_ref=fecha_ref)
        recargos = self.calcular_recargo(fecha_pago_date=fecha_ref)
        self.monto_descuentos = money(descuentos)
        self.monto_recargos = money(recargos)
        self.total_a_pagar = money(self.monto_base - self.monto_descuentos + self.monto_recargos)

    def marcar_pagada(self, fecha_pago_dt: datetime, monto_cobrado: Decimal) -> None:
        """
        Marca la cuota como pagada aplicando el cálculo al momento del cobro.
        """
        self.fecha_pago = fecha_pago_dt
        self.recalcular(fecha_pago_dt=fecha_pago_dt)
        self.pagada = True
        # (opcional) validar contra monto_cobrado


class MedioPago(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "medios_pago"
        verbose_name = "Medio de pago"
        verbose_name_plural = "Medios de pago"

    def __str__(self):
        return self.nombre


class Pago(models.Model):
    cuota = models.ForeignKey(Cuota, on_delete=models.PROTECT, related_name="pagos")
    fecha_pago = models.DateTimeField(auto_now_add=True)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    medio_pago = models.ForeignKey(MedioPago, on_delete=models.PROTECT)
    comentario = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "pagos"
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        indexes = [models.Index(fields=["fecha_pago"])]

    def __str__(self):
        return f"Pago {self.id} - {self.cuota}"


# ==========================
# Comprobantes (Drive / externos)
# ==========================
class ComprobanteDrivePago(models.Model):
    # SUG: usar otra tabla para evitar choque con "comprobantes_pago"
    marca_temporal = models.CharField(max_length=150)
    correo_electronico = models.CharField(max_length=150)
    comprobante_pago = models.CharField(max_length=150)  # id/URL de Drive
    cuil_estudiante = models.CharField(max_length=50)
    cuil_responsable_pago = models.CharField(max_length=50)

    class Meta:
        db_table = "comprobantes_pago_drive"
        verbose_name = "Comprobante (Drive)"
        verbose_name_plural = "Comprobantes (Drive)"

    def __str__(self):
        return f"Comprobante Drive {self.id} - {self.correo_electronico}"


class ComprobantePago(models.Model):
    """
    Enlace a tabla ya existente (no gestionada por Django).
    """
    marca_temporal = models.DateTimeField()
    email = models.EmailField(max_length=255)
    url_comprobante = models.URLField(max_length=500)
    cuil_alumno = models.CharField(max_length=20)
    cuil_responsable = models.CharField(max_length=20)
    ruta_local = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "comprobantes_pago"
        managed = False
        verbose_name = "Comprobante externo"
        verbose_name_plural = "Comprobantes externos"

    def __str__(self):
        return f"Comprobante ext {self.email}"
