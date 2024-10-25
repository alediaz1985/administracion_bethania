from django import forms
from .models import Documento  # Asegúrate de importar el modelo Documento

class ConsultaForm(forms.Form):
    consulta = forms.CharField(label='Ingrese DNI, CBU o palabra', max_length=255)
    fecha_inicio = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}), label='Desde')
    fecha_fin = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}), label='Hasta')

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['archivo', 'nombre']
