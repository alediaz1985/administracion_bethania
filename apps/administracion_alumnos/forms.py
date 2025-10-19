# apps/administracion_alumnos/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from .models import (
    Estudiante, Inscripcion, InformacionAcademica, ContactoEstudiante,
    SaludEstudiante, Documentacion, EstadoDocumentacion, Responsable
)

# --- Validaciones específicas que ya tenías ---
def validate_cuil(value):
    if not value.isdigit():
        raise ValidationError('El CUIL debe contener solo números.')
    if len(value) != 11:
        raise ValidationError('El CUIL debe tener exactamente 11 dígitos.')

# --- Estudiante ---
class EstudianteForm(forms.ModelForm):
    cuil_estudiante = forms.CharField(max_length=11, validators=[validate_cuil])

    class Meta:
        model = Estudiante
        fields = [
            'apellidos_estudiante','nombres_estudiante','sexo_estudiante',
            'fecha_nac_estudiante','nacionalidad_estudiante','religion_estudiante',
            'cuil_estudiante','dni_estudiante',
        ]
        widgets = {
            'sexo_estudiante': forms.Select(attrs={'class': 'form-control'}),
            'fecha_nac_estudiante': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'AAAA-MM-DD'}),
        }

# --- OneToOne ---
class InscripcionForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = [
            'marca_temporal','email_registro','foto_estudiante','num_legajo_estudiante',
            'fecha_recepcion','salita_grado_anio_estudiante','nivel_estudiante',
            'curso_anio_estudiante','turno_estudiante','nivel_ensenanza'
        ]

class InformacionAcademicaForm(forms.ModelForm):
    class Meta:
        model = InformacionAcademica
        fields = [
            'anio_cursado','donde_cursado','asignaturas_pendientes','indica_asig_pendientes',
            'tiene_hermanos_institucion','cuantos_hermanos','como_conociste_institucion','eligio_institucion'
        ]

class ContactoEstudianteForm(forms.ModelForm):
    class Meta:
        model = ContactoEstudiante
        fields = [
            'ciudad_estudiante','provincia_estudiante','barrio_estudiante','calle_estudiante',
            'n_mz_pc_estudiante','codigo_postal_estudiante','email_estudiante',
            'tel_fijo_estudiante','tel_cel_estudiante','tel_emergencia_estudiante','parentesco_estudiante'
        ]

class SaludEstudianteForm(forms.ModelForm):
    class Meta:
        model = SaludEstudiante
        fields = [
            'peso_estudiante','talla_estudiante','obra_social_estudiante','cual_osocial_estudiante',
            'problema_neurologico_estudiante','cual_prob_neurologico_estudiante',
            'problema_fisico_estudiante','certificado_medico_estudiante',
            'problema_aprendizaje_estudiante','cual_aprendizaje_estudiante',
            'atencion_medica_estudiante','alergia_estudiante'
        ]

class DocumentacionForm(forms.ModelForm):
    class Meta:
        model = Documentacion
        fields = [
            'fecha_contrato','ciudad_a_los_dias','senores1','dni_senores1','senores2','dni_senores2',
            'domicilios_senores','domicilio_especial_electronico','actuan_nombres_estudiante',
            'dni_acutan_estudiante','domicilio_actuan_estudiante','responsable_pago','dni_responsable_pago',
            'manifiesta_responsable','autoriza_facturacion_a','autoriza_imagen'
        ]

class EstadoDocumentacionForm(forms.ModelForm):
    class Meta:
        model = EstadoDocumentacion
        fields = ['estado']  # la fecha se auto-actualiza

# --- Responsables (Form + Inline Formset) ---
class ResponsableForm(forms.ModelForm):
    class Meta:
        model = Responsable
        exclude = ['estudiante']  # lo completa el formset
        widgets = {
            # puedes añadir widgets si quieres Bootstrap
        }

ResponsableFormSet = inlineformset_factory(
    parent_model=Estudiante,
    model=Responsable,
    form=ResponsableForm,
    fields=[
        'dni','apellidos','nombres','nacionalidad','fecha_nac','estado_civil','cuil',
        'nivel_instruccion','calle','n_mz_pc','barrio','ciudad','codigo_postal','provincia',
        'email','religion','tel_fijo','tel_cel','ocupacion','tel_laboral','horario_trabajo'
    ],
    extra=0,       # no agregamos filas vacías por defecto; puedes cambiar a 1+
    can_delete=True
)
