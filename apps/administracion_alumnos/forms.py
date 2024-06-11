from django import forms
from django.core.exceptions import ValidationError
from .models import Alumno

def validate_cuil(value):
    if not value.isdigit():
        raise ValidationError('El CUIL debe contener solo números.')
    if len(value) != 11:
        raise ValidationError('El CUIL debe tener exactamente 11 dígitos.')

class AlumnoForm(forms.ModelForm):
    cuil_alumno = forms.CharField(validators=[validate_cuil])
    cuil_tutor = forms.CharField(validators=[validate_cuil])

    class Meta:
        model = Alumno
        exclude = ['fecha_registro']