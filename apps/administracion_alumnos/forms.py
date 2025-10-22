# apps/administracion_alumnos/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from .models import (
    Estudiante, Inscripcion, InformacionAcademica, ContactoEstudiante,
    SaludEstudiante, Documentacion, EstadoDocumentacion, Responsable
)

# --- Validación específica que ya tenías ---
def validate_cuil(value):
    if not value.isdigit():
        raise ValidationError('El CUIL debe contener solo números.')
    if len(value) != 11:
        raise ValidationError('El CUIL debe tener exactamente 11 dígitos.')

# ------------------------------------------------------------------
# Mixin para volver NO requeridos (required=False) todos los campos
# ------------------------------------------------------------------
class OptionalFieldsMixin:
    """
    Vuelve required=False a todos los fields del form.
    Si querés forzar alguno a True, hacelo después del super().__init__().
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.required = False

# --- Estudiante ---
class EstudianteForm(OptionalFieldsMixin, forms.ModelForm):
    # Mantengo tu validador de CUIL (sigue siendo requerido por lógica de negocio)
    cuil_estudiante = forms.CharField(max_length=11, validators=[validate_cuil])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si querés que estos queden obligatorios en el form, marcá True:
        self.fields['apellidos_estudiante'].required = True
        self.fields['nombres_estudiante'].required = True
        self.fields['sexo_estudiante'].required = False  # ← puede ser opcional en edición
        self.fields['fecha_nac_estudiante'].required = False
        self.fields['nacionalidad_estudiante'].required = False
        self.fields['cuil_estudiante'].required = True   # mantenemos obligatorio
        self.fields['dni_estudiante'].required = False

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
class InscripcionForm(OptionalFieldsMixin, forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = [
            'marca_temporal','email_registro','foto_estudiante','num_legajo_estudiante',
            'fecha_recepcion','salita_grado_anio_estudiante','nivel_estudiante',
            'curso_anio_estudiante','turno_estudiante','nivel_ensenanza'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si querés algunos obligatorios en el form, marcá True:
        # self.fields['salita_grado_anio_estudiante'].required = True
        # self.fields['nivel_estudiante'].required = True
        # Por defecto todos quedan opcionales para no bloquear el guardado.


class InformacionAcademicaForm(OptionalFieldsMixin, forms.ModelForm):
    class Meta:
        model = InformacionAcademica
        fields = [
            'anio_cursado','donde_cursado','asignaturas_pendientes','indica_asig_pendientes',
            'tiene_hermanos_institucion','cuantos_hermanos','como_conociste_institucion','eligio_institucion'
        ]


class ContactoEstudianteForm(OptionalFieldsMixin, forms.ModelForm):
    class Meta:
        model = ContactoEstudiante
        fields = [
            'ciudad_estudiante','provincia_estudiante','barrio_estudiante','calle_estudiante',
            'n_mz_pc_estudiante','codigo_postal_estudiante','email_estudiante',
            'tel_fijo_estudiante','tel_cel_estudiante','tel_emergencia_estudiante','parentesco_estudiante'
        ]


class SaludEstudianteForm(OptionalFieldsMixin, forms.ModelForm):
    class Meta:
        model = SaludEstudiante
        fields = [
            'peso_estudiante','talla_estudiante','obra_social_estudiante','cual_osocial_estudiante',
            'problema_neurologico_estudiante','cual_prob_neurologico_estudiante',
            'problema_fisico_estudiante','certificado_medico_estudiante',
            'problema_aprendizaje_estudiante','cual_aprendizaje_estudiante',
            'atencion_medica_estudiante','alergia_estudiante'
        ]


class DocumentacionForm(OptionalFieldsMixin, forms.ModelForm):
    class Meta:
        model = Documentacion
        fields = [
            'fecha_contrato','ciudad_a_los_dias','senores1','dni_senores1','senores2','dni_senores2',
            'domicilios_senores','domicilio_especial_electronico','actuan_nombres_estudiante',
            'dni_acutan_estudiante','domicilio_actuan_estudiante','responsable_pago','dni_responsable_pago',
            'manifiesta_responsable','autoriza_facturacion_a','autoriza_imagen'
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si necesitás forzar alguno como obligatorio en el form, activalo:
        # self.fields['fecha_contrato'].required = True
        # self.fields['ciudad_a_los_dias'].required = True


class EstadoDocumentacionForm(OptionalFieldsMixin, forms.ModelForm):
    class Meta:
        model = EstadoDocumentacion
        fields = ['estado']  # la fecha se auto-actualiza
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si querés dejar 'estado' obligatorio en el form:
        self.fields['estado'].required = False


# --- Responsables (Form + Inline Formset) ---
class ResponsableForm(OptionalFieldsMixin, forms.ModelForm):
    class Meta:
        model = Responsable
        exclude = ['estudiante']
        widgets = {
            # acá podés agregar widgets Bootstrap si querés
        }

ResponsableFormSet = inlineformset_factory(
    Estudiante,
    Responsable,
    form=ResponsableForm,
    extra=0,
    can_delete=True
)

ResponsableFormSet = inlineformset_factory(
    parent_model=Estudiante,
    model=Responsable,
    form=ResponsableForm,
    fields=[
        'dni','apellidos','nombres','nacionalidad','fecha_nac','estado_civil','cuil',
        'nivel_instruccion','calle','n_mz_pc','barrio','ciudad','codigo_postal','provincia',
        'email','religion','tel_fijo','tel_cel','ocupacion','tel_laboral','horario_trabajo'
    ],
    extra=0,
    can_delete=True
)
