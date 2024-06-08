from django.db import models

class Alumno(models.Model):
    fecha_registro = models.DateTimeField()
    cuil_alumno = models.BigIntegerField(primary_key=True)
    apellidos_alumno = models.CharField(max_length=255)
    nombres_alumno = models.CharField(max_length=255)
    fecha_nacimiento_alumno = models.DateField()
    genero_alumno = models.CharField(max_length=50)
    domicilio_residencia_alumno = models.CharField(max_length=255)
    localidad_residencia_alumno = models.CharField(max_length=255)
    provincia_residencia_alumno = models.CharField(max_length=255)
    codigo_postal_alumno = models.CharField(max_length=10)
    numero_telefonico_alumno = models.CharField(max_length=20)
    localidad_nacimiento_alumno = models.CharField(max_length=255)
    provincia_nacimiento_alumno = models.CharField(max_length=255)
    nacionalidad_alumno = models.CharField(max_length=255)
    dni_frente_alumno = models.TextField()
    dni_dorso_alumno = models.TextField()
    nivel_cursado_alumno = models.CharField(max_length=255)
    ingreso_alumno = models.IntegerField()
    medicamento_alumno = models.TextField()
    alergia_alumno = models.TextField()
    alergico_medicamento_alumno = models.TextField()
    condicion_medica_alumno = models.TextField()
    cuil_tutor = models.BigIntegerField()
    apellido_nombre_tutor = models.CharField(max_length=255)
    telefono_tutor = models.CharField(max_length=20)
    domicilio_tutor = models.CharField(max_length=255)
    localidad_tutor = models.CharField(max_length=255)
    provincia_tutor = models.CharField(max_length=255)
    codigo_postal_tutor = models.CharField(max_length=10)
    contrato_ensenanza = models.TextField()
    ficha_inscripcion = models.TextField()

    class Meta:
        db_table = 'alumnos'  # Especifica el nombre de la tabla correcta

    def __str__(self):
        return f"{self.nombres_alumno} {self.apellidos_alumno}"
