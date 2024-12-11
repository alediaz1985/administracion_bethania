from django import forms
from .models import MontosCicloLectivo

# Formulario para agregar o editar montos de inscripción y cuota mensual
class MontosCicloLectivoForm(forms.ModelForm):
    class Meta:
        model = MontosCicloLectivo
        fields = ['monto_inscripcion', 'monto_cuota_mensual']
        widgets = {
            'monto_inscripcion': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ingrese el monto de inscripción'
            }),
            'monto_cuota_mensual': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ingrese el monto de la cuota mensual'
            }),
        }
        labels = {
            'monto_inscripcion': 'Monto de Inscripción',
            'monto_cuota_mensual': 'Monto de la Cuota Mensual',
        }


# Formulario para actualizar montos por ciclo lectivo y subnivel
class ActualizarMontosForm(forms.ModelForm):
    class Meta:
        model = MontosCicloLectivo
        fields = ['ciclo_lectivo', 'subnivel_cursado', 'monto_inscripcion', 'monto_cuota_mensual']
        labels = {
            'ciclo_lectivo': 'Ciclo Lectivo',
            'subnivel_cursado': 'Subnivel de Cursado',
            'monto_inscripcion': 'Monto de Inscripción',
            'monto_cuota_mensual': 'Monto de la Cuota Mensual',
        }
        widgets = {
            'ciclo_lectivo': forms.Select(attrs={
                'class': 'form-control', 
                'placeholder': 'Seleccione el ciclo lectivo'
            }),
            'subnivel_cursado': forms.Select(attrs={
                'class': 'form-control', 
                'placeholder': 'Seleccione el subnivel'
            }),
            'monto_inscripcion': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ingrese el monto de inscripción'
            }),
            'monto_cuota_mensual': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ingrese el monto de la cuota mensual'
            }),
        }

# Opcional: Agrega validación personalizada si es necesaria
class ValidarMontosForm(forms.ModelForm):
    class Meta:
        model = MontosCicloLectivo
        fields = ['monto_inscripcion', 'monto_cuota_mensual']

    def clean_monto_inscripcion(self):
        monto = self.cleaned_data.get('monto_inscripcion')
        if monto <= 0:
            raise forms.ValidationError('El monto de inscripción debe ser mayor a 0.')
        return monto

    def clean_monto_cuota_mensual(self):
        monto = self.cleaned_data.get('monto_cuota_mensual')
        if monto <= 0:
            raise forms.ValidationError('El monto de la cuota mensual debe ser mayor a 0.')
        return monto
