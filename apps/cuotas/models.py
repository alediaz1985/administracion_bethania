from django.db import models
from apps.administracion_alumnos.models import Alumno  # Importamos el modelo Alumno desde administracion_alumnos


# Modelo para Ciclo Lectivo
class CicloLectivo(models.Model):
    año_lectivo = models.IntegerField(verbose_name="Año Lectivo")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Fin")
    monto_inscripcion = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Monto de Inscripción")
    monto_cuota = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Monto de la Cuota")

    def __str__(self):
        return f"Ciclo {self.año_lectivo}"

    class Meta:
        db_table = 'ciclolectivo'  # Nombre personalizado para la tabla CicloLectivo
        verbose_name = "Ciclo Lectivo"
        verbose_name_plural = "Ciclos Lectivos"


# Modelo para Inscripción
class Inscripcion(models.Model):
    cuil_alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, verbose_name="Alumno")
    ciclo_lectivo = models.ForeignKey(CicloLectivo, on_delete=models.CASCADE, verbose_name="Ciclo Lectivo")
    fecha_inscripcion = models.DateField(auto_now_add=True, verbose_name="Fecha de Inscripción")
    monto_inscripcion = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto de Inscripción")
    pagada = models.BooleanField(default=False, verbose_name="Pagada")
    descuento_inscripcion = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Descuento por Inscripción")
    debe_inscripcion = models.BooleanField(default=True, verbose_name="Debe Inscripción")

    def __str__(self):
        return f'{self.cuil_alumno.nombres_alumno} {self.cuil_alumno.apellidos_alumno} - {self.ciclo_lectivo.año_lectivo}'

    class Meta:
        db_table = 'inscripcion'
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"


# Modelo para Cuota
class Cuota(models.Model):
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE, verbose_name="Inscripción")
    mes = models.IntegerField(verbose_name="Mes de la Cuota")
    monto_cuota = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto de la Cuota")
    pagado = models.BooleanField(default=False, verbose_name="Pagado")
    fecha_pago = models.DateField(null=True, blank=True, verbose_name="Fecha de Pago")
    fuera_de_termino = models.BooleanField(default=False, verbose_name="Fuera de Término")
    interes_aplicado = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Interés Aplicado")
    total_a_pagar = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total a Pagar")

    def __str__(self):
        return f'{self.inscripcion} - Mes {self.mes}'

    class Meta:
        db_table = 'cuota'  # Nombre personalizado para la tabla Cuota
        verbose_name = "Cuota"
        verbose_name_plural = "Cuotas"


# Modelo para Medios de Pago
class MedioPago(models.Model):
    nombre_medio_pago = models.CharField(max_length=100, verbose_name="Medio de Pago")

    def __str__(self):
        return self.nombre_medio_pago

    class Meta:
        db_table = 'medio_pago'  # Nombre personalizado para la tabla MedioPago
        verbose_name = "Medio de Pago"
        verbose_name_plural = "Medios de Pago"


# Modelo para Pago
class Pago(models.Model):
    cuota = models.ForeignKey(Cuota, on_delete=models.CASCADE, verbose_name="Cuota")
    fecha_pago = models.DateField(auto_now_add=True, verbose_name="Fecha de Pago")
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto Pagado")
    medio_pago = models.ForeignKey(MedioPago, on_delete=models.CASCADE, verbose_name="Medio de Pago")
    comentario = models.TextField(blank=True, null=True, verbose_name="Comentario")

    def __str__(self):
        return f'Pago por cuota {self.cuota}'

    class Meta:
        db_table = 'pago'  # Nombre personalizado para la tabla Pago
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
