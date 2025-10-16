from django.db import models

# ============================================================
# 🧍 ESTUDIANTE (Datos personales y básicos)
# ============================================================
class Estudiante(models.Model):
    SEXO_CHOICES = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
    ]

    apellidos_estudiante = models.CharField(max_length=100)
    nombres_estudiante = models.CharField(max_length=100)
    sexo_estudiante = models.CharField(max_length=9, choices=SEXO_CHOICES)
    fecha_nac_estudiante = models.CharField(max_length=100)
    nacionalidad_estudiante = models.CharField(max_length=100)
    religion_estudiante = models.CharField(max_length=100, blank=True, null=True)
    cuil_estudiante = models.CharField(max_length=50)
    dni_estudiante = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.apellidos_estudiante}, {self.nombres_estudiante}"

    class Meta:
        db_table = 'estudiante'


# ============================================================
# 🏫 INSCRIPCIÓN (Datos administrativos y académicos actuales)
# ============================================================
class Inscripcion(models.Model):
    TURNO_CHOICES = [
        ('Mañana', 'Mañana'),
        ('Tarde', 'Tarde'),
    ]

    estudiante = models.OneToOneField(Estudiante, on_delete=models.CASCADE, related_name='inscripcion')

    marca_temporal = models.CharField(max_length=100)
    email_registro = models.CharField(max_length=100)
    foto_estudiante = models.CharField(max_length=200, blank=True, null=True)
    num_legajo_estudiante = models.CharField(max_length=50, blank=True, null=True)
    fecha_recepcion = models.CharField(max_length=100, blank=True, null=True)

    salita_grado_anio_estudiante = models.CharField(max_length=100)  # “Salita/Grado/Año”
    nivel_estudiante = models.CharField(max_length=100)              # “Nivel”
    curso_anio_estudiante = models.CharField(max_length=100)
    turno_estudiante = models.CharField(max_length=20, choices=TURNO_CHOICES)
    nivel_ensenanza = models.CharField(max_length=100)

    class Meta:
        db_table = 'inscripcion'


# ============================================================
# 🎓 INFORMACIÓN ACADÉMICA (Historial y contexto)
# ============================================================
class InformacionAcademica(models.Model):
    estudiante = models.OneToOneField(Estudiante, on_delete=models.CASCADE, related_name='info_academica')

    anio_cursado = models.CharField(max_length=100)
    donde_cursado = models.CharField(max_length=100)
    asignaturas_pendientes = models.CharField(max_length=100)
    indica_asig_pendientes = models.CharField(max_length=200)
    tiene_hermanos_institucion = models.CharField(max_length=50)
    cuantos_hermanos = models.CharField(max_length=10, blank=True, null=True)
    como_conociste_institucion = models.CharField(max_length=100, blank=True, null=True)
    eligio_institucion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'info_academica'


# ============================================================
# 🏠 CONTACTO / DOMICILIO DEL ESTUDIANTE
# ============================================================
class ContactoEstudiante(models.Model):
    estudiante = models.OneToOneField(Estudiante, on_delete=models.CASCADE, related_name='contacto')

    ciudad_estudiante = models.CharField(max_length=100)
    provincia_estudiante = models.CharField(max_length=100)
    barrio_estudiante = models.CharField(max_length=100)
    calle_estudiante = models.CharField(max_length=100)
    n_mz_pc_estudiante = models.CharField(max_length=100)
    codigo_postal_estudiante = models.CharField(max_length=10)

    email_estudiante = models.CharField(max_length=100)
    tel_fijo_estudiante = models.CharField(max_length=50, blank=True, null=True)
    tel_cel_estudiante = models.CharField(max_length=50)
    tel_emergencia_estudiante = models.CharField(max_length=50)
    parentesco_estudiante = models.CharField(max_length=100)

    class Meta:
        db_table = 'contacto_estudiante'


# ============================================================
# ❤️ SALUD DEL ESTUDIANTE
# ============================================================
class SaludEstudiante(models.Model):
    estudiante = models.OneToOneField(Estudiante, on_delete=models.CASCADE, related_name='salud')

    peso_estudiante = models.CharField(max_length=20)
    talla_estudiante = models.CharField(max_length=20)
    obra_social_estudiante = models.CharField(max_length=100)
    cual_osocial_estudiante = models.CharField(max_length=100)
    problema_neurologico_estudiante = models.CharField(max_length=100)
    cual_prob_neurologico_estudiante = models.CharField(max_length=100)
    problema_fisico_estudiante = models.CharField(max_length=100)
    certificado_medico_estudiante = models.CharField(max_length=100)
    problema_aprendizaje_estudiante = models.CharField(max_length=100)
    cual_aprendizaje_estudiante = models.CharField(max_length=100)
    atencion_medica_estudiante = models.CharField(max_length=100)
    alergia_estudiante = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Salud de {self.estudiante}"

    class Meta:
        db_table = 'salud_estudiante'


# ============================================================
# 👨‍👩‍👧 RESPONSABLES (Padre, Madre, Otro)
# ============================================================
class Responsable(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='responsables')

    dni = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=100)
    nombres = models.CharField(max_length=100)
    nacionalidad = models.CharField(max_length=100)
    fecha_nac = models.CharField(max_length=100)
    estado_civil = models.CharField(max_length=100)
    cuil = models.CharField(max_length=50)
    nivel_instruccion = models.CharField(max_length=100)
    calle = models.CharField(max_length=100)
    n_mz_pc = models.CharField(max_length=100)
    barrio = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)
    provincia = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    religion = models.CharField(max_length=100, blank=True, null=True)
    tel_fijo = models.CharField(max_length=50, blank=True, null=True)
    tel_cel = models.CharField(max_length=50)
    ocupacion = models.CharField(max_length=100)
    tel_laboral = models.CharField(max_length=50)
    horario_trabajo = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"

    class Meta:
        db_table = 'responsable'


# ============================================================
# 📄 DOCUMENTACIÓN / CONTRATO EDUCATIVO
# ============================================================
class Documentacion(models.Model):
    estudiante = models.OneToOneField(Estudiante, on_delete=models.CASCADE, related_name='documentacion')

    fecha_contrato = models.CharField(max_length=100)  # “En la ciudad de ... a los días ...”
    ciudad_a_los_dias = models.CharField(max_length=100)
    senores1 = models.CharField(max_length=100)
    dni_senores1 = models.CharField(max_length=50)
    senores2 = models.CharField(max_length=100)
    dni_senores2 = models.CharField(max_length=50)
    domicilios_senores = models.CharField(max_length=150)
    domicilio_especial_electronico = models.CharField(max_length=150)
    actuan_nombres_estudiante = models.CharField(max_length=100)
    dni_acutan_estudiante = models.CharField(max_length=50)
    domicilio_actuan_estudiante = models.CharField(max_length=150)
    responsable_pago = models.CharField(max_length=100)
    dni_responsable_pago = models.CharField(max_length=50)
    manifiesta_responsable = models.CharField(max_length=200)
    autoriza_facturacion_a = models.CharField(max_length=200)
    autoriza_imagen = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"Documentación de {self.estudiante}"

    class Meta:
        db_table = 'documentacion'

# ============================================================
# ✅ ESTADO DE DOCUMENTACIÓN
# ============================================================
class EstadoDocumentacion(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Aprobado', 'Aprobado'),
    ]

    estudiante = models.OneToOneField(Estudiante, on_delete=models.CASCADE, related_name='estado_documentacion')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.estudiante} - {self.estado}"

    class Meta:
        db_table = 'estado_documentacion'

