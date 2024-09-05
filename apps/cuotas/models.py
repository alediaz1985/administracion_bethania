from django.db import models
from apps.administracion_alumnos.models import Alumno
from decimal import Decimal

class DatosGlobales(models.Model):
    año_lectivo = models.IntegerField(unique=True)
    mes_inicio = models.DateField()
    mes_fin = models.DateField()
    porcentaje_interes_mora = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    monto_inscripcion = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    importe_cuota = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Año Lectivo: {self.año_lectivo}"

class Mes(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Inscripcion(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, to_field='cuil_alumno', db_column='cuil_alumno')
    año_lectivo = models.ForeignKey(DatosGlobales, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateField(auto_now_add=True)
    monto_inscripcion = models.DecimalField(max_digits=10, decimal_places=2)
    pagado = models.BooleanField(default=False)

    def __str__(self):
        return f"Inscripción de {self.alumno} en {self.año_lectivo.año_lectivo}"

    def pagar_inscripcion(self):
        self.pagado = True
        self.save()
        self.generar_cuotas()

    def generar_cuotas(self):
        meses = Mes.objects.all()  # Obtiene todos los meses
        for mes in meses:
            Cuota.objects.get_or_create(
                inscripcion=self,
                mes=mes.nombre,
                defaults={'monto': self.año_lectivo.importe_cuota}
            )

class Cuota(models.Model):
    inscripcion = models.ForeignKey('Inscripcion', on_delete=models.CASCADE)
    mes = models.CharField(max_length=20)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(null=True, blank=True)
    pagado = models.BooleanField(default=False)
    fuera_de_termino = models.BooleanField(default=False)
    interes_por_mora = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_a_pagar = models.DecimalField(max_digits=10, decimal_places=2)

    def calcular_interes(self, already_called=False):
        if not already_called:
            # Realiza el cálculo del interés usando Decimal en lugar de float
            if self.fuera_de_termino:
                self.interes_por_mora = self.monto * Decimal('0.10')
            else:
                self.interes_por_mora = Decimal('0.00')
            
            # Actualiza el total a pagar
            self.total_a_pagar = self.monto + self.interes_por_mora
            
            # Llama a save pero pasa el flag para evitar la recursión
            self.save(already_called=True)
        else:
            # No hacer nada o manejar de otra forma
            pass

    def save(self, *args, **kwargs):
        if not kwargs.pop('already_called', False):
            self.calcular_interes(already_called=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cuota {self.mes} - {self.inscripcion.alumno} - Año: {self.inscripcion.año_lectivo.año_lectivo}"