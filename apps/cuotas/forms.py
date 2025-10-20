# apps/cuotas/forms.py
from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import (
    CicloLectivo, Nivel, Curso, TarifaNivel,
    VencimientoMensual, Beneficio, BeneficioInscripcion,
    Inscripcion, Cuota, MedioPago, Pago, money
)

# ─────────────────────────────────────────────────────────
# Ciclo
# ─────────────────────────────────────────────────────────
class CicloLectivoForm(forms.ModelForm):
    class Meta:
        model = CicloLectivo
        fields = ["anio", "fecha_inicio", "fecha_fin"]
        widgets = {
            "fecha_inicio": forms.DateInput(attrs={"type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        data = super().clean()
        ini = data.get("fecha_inicio")
        fin = data.get("fecha_fin")
        if ini and fin and fin <= ini:
            raise ValidationError("La fecha de fin debe ser posterior al inicio.")
        return data


# ─────────────────────────────────────────────────────────
# Nivel / Curso
# ─────────────────────────────────────────────────────────
class NivelForm(forms.ModelForm):
    class Meta:
        model = Nivel
        fields = ["nombre"]


class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ["nivel", "nombre", "monto_cuota_override", "monto_inscripcion_override"]


# ─────────────────────────────────────────────────────────
# Tarifas y Vencimientos
# ─────────────────────────────────────────────────────────
class TarifaNivelForm(forms.ModelForm):
    class Meta:
        model = TarifaNivel
        fields = ["ciclo", "nivel", "monto_inscripcion", "monto_cuota_mensual"]


class VencimientoMensualForm(forms.ModelForm):
    class Meta:
        model = VencimientoMensual
        fields = ["ciclo", "mes", "dia_ultimo_sin_recargo", "recargo_porcentaje"]


# ─────────────────────────────────────────────────────────
# Beneficios
# ─────────────────────────────────────────────────────────
class BeneficioForm(forms.ModelForm):
    class Meta:
        model = Beneficio
        fields = ["nombre", "tipo", "porcentaje", "monto_fijo", "prioridad", "activo"]


class BeneficioInscripcionForm(forms.ModelForm):
    class Meta:
        model = BeneficioInscripcion
        fields = ["inscripcion", "beneficio", "desde", "hasta", "activo"]
        widgets = {
            "desde": forms.DateInput(attrs={"type": "date"}),
            "hasta": forms.DateInput(attrs={"type": "date"}),
        }


# ─────────────────────────────────────────────────────────
# Inscripción (con propuesta de monto)
# ─────────────────────────────────────────────────────────
class InscripcionForm(forms.ModelForm):
    """Por defecto propone el monto de inscripción vigente."""
    class Meta:
        model = Inscripcion
        fields = ["estudiante", "ciclo", "nivel", "curso", "monto_inscripcion"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si existe la instancia, proponé el monto calculado por tu modelo
        if getattr(self, "instance", None) and self.instance.pk:
            if hasattr(self.instance, "get_monto_base_inscripcion"):
                self.fields["monto_inscripcion"].initial = self.instance.get_monto_base_inscripcion()
        # Opcional: ordená selects para mejor UX
        self.fields["ciclo"].queryset = CicloLectivo.objects.order_by("-anio")
        self.fields["nivel"].queryset = Nivel.objects.order_by("nombre")
        self.fields["curso"].queryset = Curso.objects.select_related("nivel").order_by("nivel__nombre", "nombre")


# ─────────────────────────────────────────────────────────
# Cobro puntual de cuota
# ─────────────────────────────────────────────────────────
class CuotaCobroForm(forms.Form):
    """Formulario de cobro puntual de una cuota."""
    medio_pago = forms.ModelChoiceField(queryset=MedioPago.objects.all())
    monto_cobrado = forms.DecimalField(min_value=Decimal("0.01"), decimal_places=2, max_digits=10)
    fecha_pago = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        help_text="Se usará para calcular recargos/descuentos."
    )

    def clean_monto_cobrado(self):
        return money(self.cleaned_data["monto_cobrado"])


# ─────────────────────────────────────────────────────────
# Generación de cuotas (para el panel)
# ─────────────────────────────────────────────────────────
class GenerarCuotasForm(forms.Form):
    ciclo = forms.ModelChoiceField(queryset=CicloLectivo.objects.order_by("-anio"))
    confirmar = forms.BooleanField(
        required=True,
        label="Confirmo que deseo generar/actualizar cuotas para todas las inscripciones del ciclo seleccionado."
    )
