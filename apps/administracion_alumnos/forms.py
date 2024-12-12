from django import forms
from django.core.exceptions import ValidationError
from .models import Estudiante

def validate_cuil(value):
    if not value.isdigit():
        raise ValidationError('El CUIL debe contener solo números.')
    if len(value) != 11:
        raise ValidationError('El CUIL debe tener exactamente 11 dígitos.')

class EstudianteForm(forms.ModelForm):
    cuil_estudiante = forms.CharField(
        max_length=11,
        validators=[validate_cuil],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    dni_responsable1 = forms.CharField(
        max_length=11,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DNI del Responsable 1'})
    )
    dni_responsable2 = forms.CharField(
        max_length=11,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DNI del Responsable 2'})
    )
    dni_responsable_otro = forms.CharField(
        max_length=11,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DNI del Responsable Otro'})
    )
    foto_estudiante = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    num_legajo_estudiante = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tel_fijo_estudiante = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    cual_aprendizaje_estudiante = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tel_fijo_responsable1 = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tel_fijo_responsable2 = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    apellidos_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nombres_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nacionalidad_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    fecha_nac_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.DateInput(attrs={'class': 'form-control'})
    )
    estado_civil_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    cuil_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nivel_instruccion_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    calle_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    n_mz_pc_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    barrio_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    ciudad_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    codigo_postal_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    provincia_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    religion_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tel_fijo_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tel_cel_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    ocupacion_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tel_laboral_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    horario_trab_responsable_otro = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nivel_inicial3 = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nivel_inicial4 = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nivel_inicial5 = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nivel_primario1 = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nivel_primario2 = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nivel_primario3 = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nivel_primario4 = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nivel_primario5 = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nivel_primario6 = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nivel_primario7 = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nivel_secundario1 = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nivel_secundario2 = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nivel_secundario3 = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nivel_secundario4 = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nivel_secundario5 = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    como_conociste_institucion = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    eligio_institucion = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    autoriza_imagen = forms.CharField(
        required=False,  # No obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Estudiante
        fields = '__all__'  # Incluye todos los campos del modelo
        widgets = {
            'marca_temporal': forms.TextInput(attrs={'class': 'form-control'}),
            'email_registro': forms.EmailInput(attrs={'class': 'form-control'}),
            'salita_grado_anio_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'nivel_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_recepcion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'apellidos_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo_estudiante': forms.Select(attrs={'class': 'form-control'}),
            'fecha_nac_estudiante': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nacionalidad_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'calle_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'n_mz_pc_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'barrio_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'provincia_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'dni_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'email_estudiante': forms.EmailInput(attrs={'class': 'form-control'}),
            'religion_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'tel_cel_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'tel_emergencia_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'parentesco_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'peso_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'talla_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'obra_social_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'cual_osocial_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'problema_neurologico_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'cual_prob_neurologico_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'problema_fisico_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'certificado_medico_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'problema_aprendizaje_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'atencion_medica_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'alergia_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'nacionalidad_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nac_responsable1': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estado_civil_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'cuil_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'nivel_instruccion_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'calle_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'n_mz_pc_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'barrio_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'provincia_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'email_responsable1': forms.EmailInput(attrs={'class': 'form-control'}),
            'religion_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'tel_cel_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'ocupacion_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'tel_laboral_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'horario_trab_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'nacionalidad_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nac_responsable2': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estado_civil_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'cuil_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'nivel_instruccion_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'calle_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'n_mz_pc_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'barrio_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'provincia_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'email_responsable2': forms.EmailInput(attrs={'class': 'form-control'}),
            'religion_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'tel_cel_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'ocupacion_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'tel_laboral_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'horario_trab_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'anio_cursado': forms.TextInput(attrs={'class': 'form-control'}),
            'donde_cursado': forms.TextInput(attrs={'class': 'form-control'}),
            'asignaturas_pendientes': forms.TextInput(attrs={'class': 'form-control'}),
            'indica_asig_pendientes': forms.TextInput(attrs={'class': 'form-control'}),
            'tiene_hermanos_institucion': forms.TextInput(attrs={'class': 'form-control'}),
            'cuantos_hermanos': forms.TextInput(attrs={'class': 'form-control'}),      
            'nivel_ensenanza': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad_a_los_dias': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'senores1': forms.TextInput(attrs={'class': 'form-control'}),
            'dni_senores1': forms.TextInput(attrs={'class': 'form-control'}),
            'senores2': forms.TextInput(attrs={'class': 'form-control'}),
            'dni_senores2': forms.TextInput(attrs={'class': 'form-control'}),
            'domicilios_senores': forms.TextInput(attrs={'class': 'form-control'}),
            'domicilio_especial_electronico': forms.EmailInput(attrs={'class': 'form-control'}),
            'actuan_nombres_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'dni_acutan_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'domicilio_actuan_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'responsable_pago': forms.TextInput(attrs={'class': 'form-control'}),
            'dni_responsable_pago': forms.TextInput(attrs={'class': 'form-control'}),
            'manifiesta_responsable': forms.TextInput(attrs={'class': 'form-control'}),
            'autoriza_facturacion': forms.TextInput(attrs={'class': 'form-control'}),
        }
