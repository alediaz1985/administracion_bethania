from django import forms
from apps.administracion.models import CicloLectivo, MontoNivel, Beca
from django.utils import timezone

class CicloLectivoForm(forms.ModelForm):
    class Meta:
        model = CicloLectivo
        fields = ['anio', 'fecha_inicio', 'fecha_fin', 'activo']
        widgets = {
            'anio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Año'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class MontoNivelForm(forms.ModelForm):
    class Meta:
        model = MontoNivel
        fields = [
            'ciclo',
            'nivel',
            'monto_inscripcion',
            'monto_cuota',
            'fecha_vigencia_desde',
            'activo'
        ]
        widgets = {
            'ciclo': forms.Select(attrs={'class': 'form-select'}),
            'nivel': forms.Select(attrs={'class': 'form-select'}),
            'monto_inscripcion': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'monto_cuota': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha_vigencia_desde': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        ciclo = cleaned_data.get('ciclo')
        nivel = cleaned_data.get('nivel')
        fecha_vigencia_desde = cleaned_data.get('fecha_vigencia_desde')

        # Verificar que no haya otra vigencia activa en el mismo nivel y ciclo
        if self.instance.pk is None:  # solo al crear
            existe_activo = MontoNivel.objects.filter(
                ciclo=ciclo,
                nivel=nivel,
                activo=True
            ).exists()

            if existe_activo:
                raise forms.ValidationError(
                    "Ya existe un monto activo para este nivel en este ciclo. "
                    "Desactívalo antes o crea uno con fecha posterior."
                )

        return cleaned_data
    
class BecaForm(forms.ModelForm):
    class Meta:
        model = Beca
        fields = ['nombre', 'tipo', 'valor', 'descripcion', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del beneficio'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_valor(self):
        valor = self.cleaned_data['valor']
        if valor <= 0:
            raise forms.ValidationError("El valor de la beca debe ser mayor a 0.")
        return valor
