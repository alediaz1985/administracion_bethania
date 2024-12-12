from django import forms
from .models import Documento  # Asegúrate de que el modelo Documento esté correctamente definido

class ConsultaForm(forms.Form):
    """
    Formulario para la consulta de documentos.
    """
    consulta = forms.CharField(
        label='Ingrese DNI, CBU o palabra', 
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ejemplo: 12345678 o nombre del archivo'
        })
    )
    fecha_inicio = forms.DateField(
        required=False, 
        widget=forms.TextInput(attrs={'type': 'date'}),
        label='Desde'
    )
    fecha_fin = forms.DateField(
        required=False, 
        widget=forms.TextInput(attrs={'type': 'date'}),
        label='Hasta'
    )

class DocumentoForm(forms.ModelForm):
    """
    Formulario para cargar documentos.
    """
    class Meta:
        model = Documento
        fields = ['archivo', 'nombre']
        widgets = {
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del documento'}),
        }
