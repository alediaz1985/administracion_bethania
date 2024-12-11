from django import forms
from django.core.exceptions import ValidationError
from .models import Estudiante

def validate_cuil(value):
    if not value.isdigit():
        raise ValidationError('El CUIL debe contener solo números.')
    if len(value) != 11:
        raise ValidationError('El CUIL debe tener exactamente 11 dígitos.')

class EstudianteForm(forms.ModelForm):
    cuil = forms.CharField(
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
    dni_responsableOtro = forms.CharField(
        max_length=11,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DNI del Responsable Otro'})
    )

    class Meta:
        model = Estudiante
        fields = '__all__'  # Incluye todos los campos del modelo
        widgets = {
            'marca_temporal': forms.TextInput(attrs={'class': 'form-control'}),
            'formulario_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'salita_grado_ano': forms.TextInput(attrs={'class': 'form-control'}),
            'nivel': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_legajo': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_recepcion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nacionalidad': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'calle': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_casa': forms.TextInput(attrs={'class': 'form-control'}),
            'barrio': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'provincia': forms.TextInput(attrs={'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'email_alumno': forms.EmailInput(attrs={'class': 'form-control'}),
            'religion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_fijo': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_celular': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_emergencia': forms.TextInput(attrs={'class': 'form-control'}),
            'parentesco': forms.TextInput(attrs={'class': 'form-control'}),
            'peso': forms.TextInput(attrs={'class': 'form-control'}),
            'talla': forms.TextInput(attrs={'class': 'form-control'}),
            'obra_social': forms.TextInput(attrs={'class': 'form-control'}),
            'cual_obra_social': forms.TextInput(attrs={'class': 'form-control'}),
            'problema_neurologico': forms.TextInput(attrs={'class': 'form-control'}),
            'cual_problema_neurologico': forms.TextInput(attrs={'class': 'form-control'}),
            'problema_actividad_fisica': forms.TextInput(attrs={'class': 'form-control'}),
            'certificado_medico': forms.TextInput(attrs={'class': 'form-control'}),
            'problema_aprendizaje': forms.TextInput(attrs={'class': 'form-control'}),
            'cual_problema_aprendizaje': forms.TextInput(attrs={'class': 'form-control'}),
            'atencion_medica': forms.TextInput(attrs={'class': 'form-control'}),
            'alergico': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'nacionalidad_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento_responsable1': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
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
            'telefono_fijo_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_celular_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'ocupacion_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_laboral_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'horario_laboral_responsable1': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'nacionalidad_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento_responsable2': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
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
            'telefono_fijo_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_celular_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'ocupacion_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_laboral_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'horario_laboral_responsable2': forms.TextInput(attrs={'class': 'form-control'}),
            'nivel_ensenanza': forms.TextInput(attrs={'class': 'form-control'}),
            'contrato_fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'contrato_senores1': forms.TextInput(attrs={'class': 'form-control'}),
            'contrato_dniSenores1': forms.TextInput(attrs={'class': 'form-control'}),
            'contrato_senores2': forms.TextInput(attrs={'class': 'form-control'}),
            'contrato_dniSenores2': forms.TextInput(attrs={'class': 'form-control'}),
            'contrato_domicilioSenores': forms.TextInput(attrs={'class': 'form-control'}),
            'contrato_emailSenores': forms.EmailInput(attrs={'class': 'form-control'}),
            'contrato_representacionAlumno': forms.TextInput(attrs={'class': 'form-control'}),
            'contrato_dniAlumno': forms.TextInput(attrs={'class': 'form-control'}),
            'contrato_domicilioAlumno': forms.TextInput(attrs={'class': 'form-control'}),
            'contrato_responsable': forms.TextInput(attrs={'class': 'form-control'}),
            'contrato_dniResponsable': forms.TextInput(attrs={'class': 'form-control'}),
            'contrato_cumplimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'contrato_autorizacionFacturacion': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen_autorizado': forms.FileInput(attrs={'class': 'form-control'}),
        }
