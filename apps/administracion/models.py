from django.db import models

# Create your models here.
# administracion/models.py

from django.db import models
from apps.administracion_alumnos.models import Estudiante

class Nivel(models.Model):
    nombre = models.CharField(max_length=50)  # Ej: Jardin, Primaria, etc.

    def __str__(self):
        return self.nombre

class CicloLectivo(models.Model):
    anio = models.IntegerField(unique=True)
    habilitado = models.BooleanField(default=False)

    def __str__(self):
        return str(self.anio)

class NivelCiclo(models.Model):
    ciclo = models.ForeignKey(CicloLectivo, on_delete=models.CASCADE, related_name='niveles')
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE, related_name='ciclos')
    precio_inscripcion = models.DecimalField(max_digits=10, decimal_places=2)
    precio_cuota = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nivel.nombre} - {self.ciclo.anio}"

class Inscripcion(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='inscripciones')
    nivel_ciclo = models.ForeignKey(NivelCiclo, on_delete=models.CASCADE, related_name='inscripciones')
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.estudiante} - {self.nivel_ciclo}"

class PagoInscripcion(models.Model):
    inscripcion = models.OneToOneField(Inscripcion, on_delete=models.CASCADE, related_name='pago_inscripcion')
    fecha_pago = models.DateField()
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=50)

    def __str__(self):
        return f"Pago inscripción - {self.inscripcion}"

class Cuota(models.Model):
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE, related_name='cuotas')
    numero = models.PositiveIntegerField()  # Ej: 1, 2, ..., 10
    vencimiento = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Cuota {self.numero} - {self.inscripcion}"

class Pago(models.Model):
    cuota = models.ForeignKey(Cuota, on_delete=models.CASCADE, related_name='pagos')
    fecha_pago = models.DateField()
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=50)

    def __str__(self):
        return f"Pago cuota {self.cuota.numero} - {self.cuota.inscripcion.estudiante}"
