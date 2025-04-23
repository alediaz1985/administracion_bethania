from django.db import models
from apps.administracion_alumnos.models import Estudiante  # Importa el modelo Estudiante


# Modelo para Ciclo Lectivo
class CicloLectivo(models.Model):
    año_lectivo = models.IntegerField(verbose_name="Año Lectivo")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Fin")

    def __str__(self):
        return f"Ciclo {self.año_lectivo}"

    class Meta:
        db_table = 'ciclolectivo'
        verbose_name = "Ciclo Lectivo"
        verbose_name_plural = "Ciclos Lectivos"


# Modelo para Nivel de Cursado
class NivelCursado(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Nivel")
    descripcion = models.TextField(verbose_name="Descripción del Nivel")

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'nivel_cursado'
        verbose_name = "Nivel de Cursado"
        verbose_name_plural = "Niveles de Cursado"


# Modelo para SubNivel (Ej. Sala 3, 4, Grados o Carreras)
class SubNivelCursado(models.Model):
    nivel_cursado = models.ForeignKey(NivelCursado, on_delete=models.CASCADE, verbose_name="Nivel de Cursado")
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Subnivel")

    def __str__(self):
        return f'{self.nivel_cursado.nombre} - {self.nombre}'

    class Meta:
        db_table = 'subnivel_cursado'
        verbose_name = "Subnivel de Cursado"
        verbose_name_plural = "Subniveles de Cursado"


# Modelo para Montos de Ciclo Lectivo por Subnivel
class MontosCicloLectivo(models.Model):
    ciclo_lectivo = models.ForeignKey(CicloLectivo, on_delete=models.CASCADE, verbose_name="Ciclo Lectivo")
    subnivel_cursado = models.ForeignKey(SubNivelCursado, on_delete=models.CASCADE, verbose_name="Subnivel")
    monto_inscripcion = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto de Inscripción")
    monto_cuota_mensual = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto de la Cuota Mensual")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")  # Auto-actualiza cada vez que se guarda

    def __str__(self):
        return f'{self.ciclo_lectivo.año_lectivo} - {self.subnivel_cursado.nombre}'

    class Meta:
        db_table = 'montos_ciclolectivo'
        verbose_name = "Montos del Ciclo Lectivo"
        verbose_name_plural = "Montos del Ciclo Lectivo"


# Modelo para Inscripción
class Inscripcion(models.Model):
    cuil_alumno = models.ForeignKey(Estudiante, on_delete=models.CASCADE, verbose_name="Estudiante")  # Cambiado Alumno -> Estudiante
    ciclo_lectivo = models.ForeignKey(CicloLectivo, on_delete=models.CASCADE, verbose_name="Ciclo Lectivo")
    subnivel_cursado = models.ForeignKey(SubNivelCursado, on_delete=models.CASCADE, default=1, verbose_name="Subnivel Cursado")
    fecha_inscripcion = models.DateField(auto_now_add=True, verbose_name="Fecha de Inscripción")
    monto_inscripcion = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto de Inscripción")
    pagada = models.BooleanField(default=False)
    descuento_inscripcion = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Descuento por Inscripción")

    def __str__(self):
        return f'{self.cuil_alumno.nombres_estudiante} {self.cuil_alumno.apellidos_estudiante} - {self.ciclo_lectivo.año_lectivo}'

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
        db_table = 'cuota'
        verbose_name = "Cuota"
        verbose_name_plural = "Cuotas"


# Modelo para Medios de Pago
class MedioPago(models.Model):
    nombre_medio_pago = models.CharField(max_length=100, verbose_name="Medio de Pago")

    def __str__(self):
        return self.nombre_medio_pago

    class Meta:
        db_table = 'medio_pago'
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
        db_table = 'pago'
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"


class ComprobanteDrivePago(models.Model):
    marca_temporal = models.CharField(max_length=150, verbose_name="Marca Temporal")
    correo_electronico = models.CharField(max_length=150, verbose_name="Dirección de Correo Electrónico")
    comprobante_pago = models.CharField(max_length=150, verbose_name="Adjunte el Comprobante de Pagos")
    cuil_estudiante = models.CharField(max_length=50, verbose_name="CUIL del Estudiante")
    cuil_responsable_pago = models.CharField(max_length=50, verbose_name="CUIL del Responsable de Pago")

    def __str__(self):
        return f"Comprobante {self.id} - {self.correo_electronico}"

    class Meta:
        db_table = 'comprobante_de_pago'
        verbose_name = "Comprobante de Pago"
        verbose_name_plural = "Comprobantes de Pago"
        


