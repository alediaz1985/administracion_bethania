from django import forms
from .models import Documento
from apps.administracion_alumnos.models import Estudiante, Responsable

class ConsultaForm(forms.Form):
    consulta = forms.CharField(
        label="Ingrese DNI, CBU o palabra",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "consulta__input",
            "placeholder": "Ej.: 12345678 o nombre del archivo"
        })
    )
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={"type": "date", "class": "consulta__input-fecha"}),
        label="Desde"
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={"type": "date", "class": "consulta__input-fecha"}),
        label="Hasta"
    )

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = [
            "correo",
            "archivo",
            "nombre",
            "estudiante",
            "cuil_estudiante",
            "responsable",
            "cuil_responsable",
        ]
        widgets = {
            "correo": forms.EmailInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "archivo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del comprobante"}),
            "estudiante": forms.Select(attrs={"class": "form-select"}),
            "cuil_estudiante": forms.TextInput(attrs={"class": "form-control", "pattern": r"\d{11}", "maxlength": "11"}),
            "responsable": forms.Select(attrs={"class": "form-select"}),
            "cuil_responsable": forms.TextInput(attrs={"class": "form-control", "pattern": r"\d{11}", "maxlength": "11"}),
        }

    def __init__(self, *args, **kwargs):
        correo_institucional = kwargs.pop("correo_institucional", None)
        super().__init__(*args, **kwargs)
        if correo_institucional:
            self.fields["correo"].initial = correo_institucional

        # Si hay estudiante seleccionado (POST), limitá los responsables a los de ese alumno
        if "estudiante" in self.data:
            try:
                est_id = int(self.data.get("estudiante"))
                self.fields["responsable"].queryset = Responsable.objects.filter(estudiante_id=est_id)
            except Exception:
                self.fields["responsable"].queryset = Responsable.objects.none()
        elif self.instance.pk and self.instance.estudiante_id:
            self.fields["responsable"].queryset = Responsable.objects.filter(estudiante=self.instance.estudiante)
        else:
            self.fields["responsable"].queryset = Responsable.objects.all()

    def clean_cuil_estudiante(self):
        cuil = (self.cleaned_data.get("cuil_estudiante") or "").strip()
        if not cuil.isdigit() or len(cuil) != 11:
            raise forms.ValidationError("El CUIL del estudiante debe tener exactamente 11 dígitos numéricos.")
        return cuil

    def clean_cuil_responsable(self):
        cuil = (self.cleaned_data.get("responsable_pago") or "").strip()
        if not cuil.isdigit() or len(cuil) != 11:
            raise forms.ValidationError("El CUIL del responsable debe tener exactamente 11 dígitos numéricos.")
        return cuil

    def clean(self):
        cleaned = super().clean()
        estudiante = cleaned.get("estudiante")
        responsable = cleaned.get("responsable")
        cuil_est = cleaned.get("cuil_estudiante")
        cuil_resp = cleaned.get("responsable_pago")

        # CUIL estudiante debe coincidir con el del modelo Estudiante
        if estudiante and cuil_est:
            if (estudiante.cuil_estudiante or "").replace("-", "").strip() != cuil_est:
                self.add_error("cuil_estudiante", "El CUIL no coincide con el CUIL del estudiante seleccionado.")

        # Responsable debe pertenecer al Estudiante
        if estudiante and responsable and responsable.estudiante_id != estudiante.id:
            self.add_error("responsable", "El responsable seleccionado no pertenece a este estudiante.")

        # CUIL responsable debe coincidir con el del modelo Responsable
        if responsable and cuil_resp:
            if (responsable.cuil or "").replace("-", "").strip() != cuil_resp:
                self.add_error("responsable_pago", "El CUIL no coincide con el CUIL del responsable seleccionado.")

        return cleaned
