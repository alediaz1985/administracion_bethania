from django.db import models

class Estudiante(models.Model):

    # Definimos las opciones para el campo 'sexo_estudiante'
    SEXO_CHOICES = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
    ]

    id = models.AutoField(primary_key=True)  # Auto incremental
    marca_temporal = models.CharField(max_length=100)
    email_registro = models.CharField(max_length=100)
    foto_estudiante = models.CharField(max_length=100, null=True, blank=True)
    salita_grado_anio_estudiante = models.CharField(max_length=100)
    nivel_estudiante = models.CharField(max_length=100)
    num_legajo_estudiante = models.CharField(max_length=100, blank=True, null=True)
    fecha_recepcion = models.CharField(max_length=100, blank=True, null=True)
    apellidos_estudiante = models.CharField(max_length=100)
    nombres_estudiante = models.CharField(max_length=100)
    sexo_estudiante = models.CharField(
        max_length=9,
        choices=SEXO_CHOICES,  # Lista de opciones definidas arriba
        default='Masculino',  # Valor por defecto, puedes cambiarlo si es necesario
    )
    fecha_nac_estudiante = models.CharField(max_length=100)
    nacionalidad_estudiante = models.CharField(max_length=100)
    ciudad_estudiante = models.CharField(max_length=100)
    calle_estudiante = models.CharField(max_length=100)
    n_mz_pc_estudiante = models.CharField(max_length=100)
    barrio_estudiante = models.CharField(max_length=100)
    codigo_postal_estudiante = models.CharField(max_length=100)
    provincia_estudiante = models.CharField(max_length=100)
    cuil_estudiante = models.CharField(max_length=100)
    dni_estudiante = models.CharField(max_length=100)
    email_estudiante = models.CharField(max_length=100)
    religion_estudiante = models.CharField(max_length=100)
    tel_fijo_estudiante = models.CharField(max_length=100, blank=True, null=True)
    tel_cel_estudiante = models.CharField(max_length=100)
    tel_emergencia_estudiante = models.CharField(max_length=100)
    parentesco_estudiante = models.CharField(max_length=100)
    peso_estudiante = models.CharField(max_length=100)
    talla_estudiante = models.CharField(max_length=100)
    obra_social_estudiante = models.CharField(max_length=100)
    cual_osocial_estudiante = models.CharField(max_length=100)
    problema_neurologico_estudiante = models.CharField(max_length=100)
    cual_prob_neurologico_estudiante = models.CharField(max_length=100)
    problema_fisico_estudiante = models.CharField(max_length=100)
    certificado_medico_estudiante = models.CharField(max_length=100)
    problema_aprendizaje_estudiante = models.CharField(max_length=100)
    cual_aprendizaje_estudiante = models.CharField(max_length=100)
    atencion_medica_estudiante = models.CharField(max_length=100)
    alergia_estudiante = models.CharField(max_length=100)
    dni_responsable1 = models.CharField(max_length=100)
    apellidos_responsable1 = models.CharField(max_length=100)
    nombres_responsable1 = models.CharField(max_length=100)
    nacionalidad_responsable1 = models.CharField(max_length=100)
    fecha_nac_responsable1 = models.CharField(max_length=100)
    estado_civil_responsable1 = models.CharField(max_length=100)
    cuil_responsable1 = models.CharField(max_length=100)
    nivel_instruccion_responsable1 = models.CharField(max_length=100)
    calle_responsable1 = models.CharField(max_length=100)
    n_mz_pc_responsable1 = models.CharField(max_length=100)
    barrio_responsable1 = models.CharField(max_length=100)
    ciudad_responsable1 = models.CharField(max_length=100)
    codigo_postal_responsable1 = models.CharField(max_length=100)
    provincia_responsable1 = models.CharField(max_length=100)
    email_responsable1 = models.CharField(max_length=100)
    religion_responsable1 = models.CharField(max_length=100)
    tel_fijo_responsable1 = models.CharField(max_length=100, blank=True, null=True)
    tel_cel_responsable1 = models.CharField(max_length=100)
    ocupacion_responsable1 = models.CharField(max_length=100)
    tel_laboral_responsable1 = models.CharField(max_length=100)
    horario_trab_responsable1 = models.CharField(max_length=100)
    dni_responsable2 = models.CharField(max_length=100)
    apellidos_responsable2 = models.CharField(max_length=100)
    nombres_responsable2 = models.CharField(max_length=100)
    nacionalidad_responsable2 = models.CharField(max_length=100)
    fecha_nac_responsable2 = models.CharField(max_length=100)
    estado_civil_responsable2 = models.CharField(max_length=100)
    cuil_responsable2 = models.CharField(max_length=100)
    nivel_instruccion_responsable2 = models.CharField(max_length=100)
    calle_responsable2 = models.CharField(max_length=100)
    n_mz_pc_responsable2 = models.CharField(max_length=100)
    barrio_responsable2 = models.CharField(max_length=100)
    ciudad_responsable2 = models.CharField(max_length=100)
    codigo_postal_responsable2 = models.CharField(max_length=100)
    provincia_responsable2 = models.CharField(max_length=100)
    email_responsable2 = models.CharField(max_length=100)
    religion_responsable2 = models.CharField(max_length=100)
    tel_fijo_responsable2 = models.CharField(max_length=100, blank=True, null=True)
    tel_cel_responsable2 = models.CharField(max_length=100)
    ocupacion_responsable2 = models.CharField(max_length=100)
    tel_laboral_responsable2 = models.CharField(max_length=100)
    horario_trab_responsable2 = models.CharField(max_length=100)
    dni_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    apellidos_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    nombres_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    nacionalidad_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    fecha_nac_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    estado_civil_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    cuil_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    nivel_instruccion_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    calle_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    n_mz_pc_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    barrio_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    ciudad_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    codigo_postal_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    provincia_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    email_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    religion_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    tel_fijo_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    tel_cel_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    ocupacion_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    tel_laboral_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    horario_trab_responsable_otro = models.CharField(max_length=100, blank=True, null=True)
    anio_cursado = models.CharField(max_length=100)
    donde_cursado = models.CharField(max_length=100)
    asignaturas_pendientes = models.CharField(max_length=100)
    indica_asig_pendientes = models.CharField(max_length=100)
    tiene_hermanos_institucion = models.CharField(max_length=100)
    cuantos_hermanos = models.CharField(max_length=100, blank=True, null=True)
    nivel_inicial3 = models.CharField(max_length=100, blank=True, null=True)
    nivel_inicial4 = models.CharField(max_length=100, blank=True, null=True)
    nivel_inicial5 = models.CharField(max_length=100, blank=True, null=True)
    nivel_primario1 = models.CharField(max_length=100, blank=True, null=True)
    nivel_primario2 = models.CharField(max_length=100, blank=True, null=True)
    nivel_primario3 = models.CharField(max_length=100, blank=True, null=True)
    nivel_primario4 = models.CharField(max_length=100, blank=True, null=True)
    nivel_primario5 = models.CharField(max_length=100, blank=True, null=True)
    nivel_primario6 = models.CharField(max_length=100, blank=True, null=True)
    nivel_primario7 = models.CharField(max_length=100, blank=True, null=True)
    nivel_secundario1 = models.CharField(max_length=100, blank=True, null=True)
    nivel_secundario2 = models.CharField(max_length=100, blank=True, null=True)
    nivel_secundario3 = models.CharField(max_length=100, blank=True, null=True)
    nivel_secundario4 = models.CharField(max_length=100, blank=True, null=True)
    nivel_secundario5 = models.CharField(max_length=100, blank=True, null=True)
    como_conociste_institucion = models.CharField(max_length=100, blank=True, null=True)
    eligio_institucion = models.CharField(max_length=100, blank=True, null=True)
    nivel_ensenanza = models.CharField(max_length=100)
    ciudad_a_los_dias = models.CharField(max_length=100)
    senores1 = models.CharField(max_length=100)
    dni_senores1 = models.CharField(max_length=100)
    senores2 = models.CharField(max_length=100)
    dni_senores2 = models.CharField(max_length=100)
    domicilios_senores = models.CharField(max_length=100)
    domicilio_especial_electronico = models.CharField(max_length=100)
    actuan_nombres_estudiante = models.CharField(max_length=100)
    dni_acutan_estudiante = models.CharField(max_length=100)
    domicilio_actuan_estudiante = models.CharField(max_length=100)
    responsable_pago = models.CharField(max_length=100)
    dni_responsable_pago = models.CharField(max_length=100)
    manifiesta_responsable = models.CharField(max_length=100)
    autoriza_facturacion = models.CharField(max_length=100)
    autoriza_imagen = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.apellidos_estudiante}, {self.nombres_estudiante}"

    class Meta:
        db_table = 'estudiante'

class EstadoDocumentacion(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
    ]

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='estados_documentacion')
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.estudiante} - {self.estado}"

    class Meta:
        db_table = 'estado_documentacion'



# 'num_legajo_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
# 'tel_fijo_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
# 'cual_aprendizaje_estudiante': forms.TextInput(attrs={'class': 'form-control'}),

# 'tel_fijo_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
# 'tel_fijo_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
# 'apellidos_responsable_otro': forms.TextInput(attrs={'class': 'form-control'}),
# 'nombres_responsable_otro': forms.TextInput(attrs={'class': 'form-control'}),
# 'nacionalidad_responsable_otro': forms.TextInput(attrs={'class': 'form-control'}),
# 'fecha_nac_responsable_otro': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
# 'estado_civil_responsable_otro': forms.TextInput(attrs={'class': 'form-control'}),
# 'cuil_responsable_otro': forms.TextInput(attrs={'class': 'form-control'}),
# 'nivel_instruccion_responsable_otro': forms.TextInput(attrs={'class': 'form-control'}),
# 'calle_responsable_otro': forms.TextInput(attrs={'class': 'form-control'}),
# 'n_mz_pc_responsable_otro': forms.TextInput(attrs={'class': 'form-control'}),
# 'barrio_responsable_otro': forms.TextInput(attrs={'class': 'form-control'}),
# 'ciudad_responsable_otro': forms.TextInput(attrs={'class': 'form-control'}),
# 'codigo_postal_responsable_otro': forms.TextInput(attrs={'class': 'form-control'}),
# 'provincia_responsable_otro': forms.TextInput(attrs={'class': 'form-control'}),
# 'email_responsable_otro': forms.EmailInput(attrs={'class': 'form-control'}),
# 'religion_responsable_otro': forms.TextInput(attrs={'class': 'form-control'}),
# 'tel_fijo_responsable_otro': forms.TextInput(attrs={'class': 'form-control'}),
# 'tel_cel_responsable_otro': forms.TextInput(attrs={'class': 'form-control'}),
# 'ocupacion_responsable_otro': forms.TextInput(attrs={'class': 'form-control'}),
# 'tel_laboral_responsable_otro': forms.TextInput(attrs={'class': 'form-control'}),
# 'horario_trab_responsable_otro': forms.TextInput(attrs={'class': 'form-control'}),


# 'nivel_inicial3': forms.TextInput(attrs={'class': 'form-control'}),
# 'nivel_inicial4': forms.TextInput(attrs={'class': 'form-control'}),
# 'nivel_inicial5': forms.TextInput(attrs={'class': 'form-control'}),
# 'nivel_primario1': forms.TextInput(attrs={'class': 'form-control'}),
# 'nivel_primario2': forms.TextInput(attrs={'class': 'form-control'}),
# 'nivel_primario3': forms.TextInput(attrs={'class': 'form-control'}),
# 'nivel_primario4': forms.TextInput(attrs={'class': 'form-control'}),
# 'nivel_primario5': forms.TextInput(attrs={'class': 'form-control'}),
# 'nivel_primario6': forms.TextInput(attrs={'class': 'form-control'}),
# 'nivel_primario7': forms.TextInput(attrs={'class': 'form-control'}),
# 'nivel_secundario1': forms.TextInput(attrs={'class': 'form-control'}),
# 'nivel_secundario2': forms.TextInput(attrs={'class': 'form-control'}),
# 'nivel_secundario3': forms.TextInput(attrs={'class': 'form-control'}),
# 'nivel_secundario4': forms.TextInput(attrs={'class': 'form-control'}),
# 'nivel_secundario5': forms.TextInput(attrs={'class': 'form-control'}),


# 'como_conociste_institucion': forms.TextInput(attrs={'class': 'form-control'}),
# 'eligio_institucion': forms.TextInput(attrs={'class': 'form-control'}),