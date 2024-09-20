from django import forms
from .models import Documento  # Asegúrate de importar el modelo Documento

class ConsultaForm(forms.Form):
    consulta = forms.CharField(label='Ingrese DNI, CBU o palabra', max_length=255)

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['archivo', 'nombre']
