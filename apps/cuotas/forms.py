from django import forms
from .models import MontosCicloLectivo

class MontosCicloLectivoForm(forms.ModelForm):
    class Meta:
        model = MontosCicloLectivo
        fields = ['monto_inscripcion', 'monto_cuota_mensual']


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