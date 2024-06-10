from django.db import models

class Docente(models.Model):
    cuil = models.CharField(max_length=20, primary_key=True)
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=50)
    direccion = models.CharField(max_length=255)
    provincia = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    nacionalidad = models.CharField(max_length=100)
    
    titulo_academico = models.CharField(max_length=255, blank=True, null=True)
    especialidad = models.CharField(max_length=255, blank=True, null=True)
    anos_experiencia = models.IntegerField(blank=True, null=True)
    idiomas = models.CharField(max_length=255, blank=True, null=True)
    certificaciones = models.CharField(max_length=255, blank=True, null=True)
    cursos_realizados = models.CharField(max_length=255, blank=True, null=True)
    
    fecha_ingreso = models.DateField()
    numero_legajo = models.CharField(max_length=50, unique=True)
    cargo = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    horario_trabajo = models.CharField(max_length=100)
    
    salario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_ultimo_ascenso = models.DateField(blank=True, null=True)
    estado_laboral = models.CharField(max_length=50, blank=True, null=True)
    contacto_emergencia = models.CharField(max_length=255, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    cuil_supervisor = models.CharField(max_length=20, blank=True, null=True)
    cursos_asignados = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.cuil})"
    
    class Meta:
        db_table = 'docentes'
