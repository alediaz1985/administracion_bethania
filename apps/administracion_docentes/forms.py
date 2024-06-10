from django import forms
from .models import Docente

class DocenteForm(forms.ModelForm):
    class Meta:
        model = Docente
        fields = [
            'cuil', 'nombre', 'apellido', 'fecha_nacimiento', 'genero', 'direccion', 
            'provincia', 'telefono', 'email', 'nacionalidad', 'titulo_academico', 
            'especialidad', 'anos_experiencia', 'idiomas', 'certificaciones', 
            'cursos_realizados', 'fecha_ingreso', 'numero_legajo', 'cargo', 
            'departamento', 'horario_trabajo', 'salario', 'fecha_ultimo_ascenso', 
            'estado_laboral', 'contacto_emergencia', 'observaciones', 'cuil_supervisor', 
            'cursos_asignados'
        ]
