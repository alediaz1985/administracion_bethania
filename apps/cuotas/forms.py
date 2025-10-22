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

from django import forms
from .models import Nivel, Curso

class NivelForm(forms.ModelForm):
    class Meta:
        model = Nivel
        fields = ["nombre"]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej.: Inicial, Primario, Secundario",
                "autofocus": "autofocus"
            })
        }

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ["nombre", "nivel"]  # ajustá si tu Curso tiene más campos
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej.: 1º A, 2º B, Sala 4, etc."
            }),
            "nivel": forms.Select(attrs={"class": "form-select"})
        }


from calendar import monthrange
from decimal import Decimal
from django import forms
from django.core.exceptions import ValidationError

from .models import VencimientoMensual


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
        labels = {
            "ciclo": "Ciclo lectivo",
            "mes": "Mes (1-12)",
            "dia_ultimo_sin_recargo": "Día último sin recargo",
            "recargo_porcentaje": "Recargo (%)",
        }
        widgets = {
            "ciclo": forms.Select(attrs={"class": "form-control"}),
            "mes": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 12}),
            "dia_ultimo_sin_recargo": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 31}),
            "recargo_porcentaje": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
        }

    def clean(self):
        cleaned = super().clean()
        ciclo = cleaned.get("ciclo")
        mes = cleaned.get("mes")
        dia = cleaned.get("dia_ultimo_sin_recargo")
        if ciclo and mes and dia:
            try:
                y = int(ciclo.anio)
                ultimo = monthrange(y, mes)[1]
                if dia > ultimo:
                    raise ValidationError({
                        "dia_ultimo_sin_recargo": f"Para {y}-{mes:02d} el último día real es {ultimo}."
                    })
            except Exception:
                pass
        return cleaned

    def clean_recargo_porcentaje(self):
        p = self.cleaned_data.get("recargo_porcentaje")
        if p is None:
            return p
        if p < Decimal("0"):
            raise ValidationError("El recargo no puede ser negativo.")
        return p



# ─────────────────────────────────────────────────────────
# Beneficios
# ─────────────────────────────────────────────────────────
from django import forms
from django.core.exceptions import ValidationError
from .models import Beneficio, BeneficioInscripcion

class BeneficioForm(forms.ModelForm):
    class Meta:
        model = Beneficio
        fields = [
            "nombre", "tipo", "porcentaje", "monto_fijo", "prioridad", "activo"
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "maxlength": 120}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "porcentaje": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0", "max": "100"}),
            "monto_fijo": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "prioridad": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned = super().clean()
        porcentaje = cleaned.get("porcentaje")
        monto_fijo = cleaned.get("monto_fijo")

        # Al menos uno
        if (porcentaje is None or porcentaje == 0) and (monto_fijo is None or monto_fijo == 0):
            raise ValidationError("Debés especificar al menos un valor: porcentaje (>0) y/o monto fijo (>0).")

        # Rangos
        if porcentaje is not None:
            if porcentaje < 0 or porcentaje > 100:
                self.add_error("porcentaje", "El porcentaje debe estar entre 0 y 100.")
        if monto_fijo is not None:
            if monto_fijo < 0:
                self.add_error("monto_fijo", "El monto fijo no puede ser negativo.")

        return cleaned


class BeneficioInscripcionForm(forms.ModelForm):
    class Meta:
        model = BeneficioInscripcion
        fields = ["inscripcion", "beneficio", "desde", "hasta", "activo"]
        widgets = {
            "inscripcion": forms.Select(attrs={"class": "form-select"}),
            "beneficio": forms.Select(attrs={"class": "form-select"}),
            "desde": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "hasta": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned = super().clean()
        desde = cleaned.get("desde")
        hasta = cleaned.get("hasta")
        beneficio = cleaned.get("beneficio")

        if desde and hasta and hasta < desde:
            raise ValidationError("El rango de fechas es inválido: 'hasta' no puede ser anterior a 'desde'.")

        # Beneficio debe estar activo al momento de asignarlo (política sugerida)
        if beneficio and not beneficio.activo:
            self.add_error("beneficio", "El beneficio seleccionado está inactivo.")

        return cleaned

# ─────────────────────────────────────────────────────────
# Inscripción (con propuesta de monto)
# ─────────────────────────────────────────────────────────
from django import forms
from django.core.exceptions import ValidationError
from .models import Inscripcion, Cuota, TarifaNivel

class InscripcionForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = ["estudiante", "ciclo", "nivel", "curso", "monto_inscripcion"]
        widgets = {
            "estudiante": forms.Select(attrs={"class": "form-select"}),
            "ciclo": forms.Select(attrs={"class": "form-select"}),
            "nivel": forms.Select(attrs={"class": "form-select"}),
            "curso": forms.Select(attrs={"class": "form-select"}),
            "monto_inscripcion": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
        }

    def clean(self):
        cleaned = super().clean()
        ciclo = cleaned.get("ciclo")
        nivel = cleaned.get("nivel")
        curso = cleaned.get("curso")
        # Validar existencia de tarifa si no hay override en curso
        if ciclo and nivel and curso and curso.monto_inscripcion_override is None:
            try:
                TarifaNivel.objects.get(ciclo=ciclo, nivel=nivel)
            except TarifaNivel.DoesNotExist:
                raise ValidationError("No existe TarifaNivel para ese ciclo y nivel. Definila o poné override en curso.")
        return cleaned


class CuotaForm(forms.ModelForm):
    class Meta:
        model = Cuota
        fields = ["monto_base", "monto_descuentos", "monto_recargos", "total_a_pagar", "pagada", "fecha_pago"]
        widgets = {
            "monto_base": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "monto_descuentos": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "monto_recargos": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "total_a_pagar": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "pagada": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "fecha_pago": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        }

    def clean(self):
        cleaned = super().clean()
        total = cleaned.get("total_a_pagar")
        base = cleaned.get("monto_base")
        if total is not None and total < 0:
            self.add_error("total_a_pagar", "El total no puede ser negativo.")
        if base is not None and base < 0:
            self.add_error("monto_base", "El monto base no puede ser negativo.")
        return cleaned

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


# ─────────────────────────────────────────────────────────
# Curso (con validaciones y UX mejorada)
# ─────────────────────────────────────────────────────────
class CursoForm(forms.ModelForm):
    # Declaramos explícitamente para controlar validaciones/UX
    nombre = forms.CharField(
        label="Nombre del curso",
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ej.: 1° A, 2° B, Sala 4, etc.",
            "autofocus": "autofocus",
            "autocomplete": "off"
        }),
        help_text="Usá un nombre distintivo dentro del nivel (se valida unicidad por nivel)."
    )

    monto_cuota_override = forms.DecimalField(
        label="Monto mensual (override)",
        required=False,
        min_value=Decimal("0"),
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Dejar vacío para usar la tarifa del nivel",
            "step": "0.01",
            "inputmode": "decimal"
        }),
        help_text="Si lo dejás vacío, se usa la tarifa mensual definida para el nivel."
    )

    monto_inscripcion_override = forms.DecimalField(
        label="Inscripción (override)",
        required=False,
        min_value=Decimal("0"),
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Dejar vacío para usar la tarifa del nivel",
            "step": "0.01",
            "inputmode": "decimal"
        }),
        help_text="Si lo dejás vacío, se usa la inscripción definida para el nivel."
    )

    class Meta:
        model = Curso
        fields = ["nivel", "nombre", "monto_cuota_override", "monto_inscripcion_override"]
        widgets = {
            "nivel": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "nivel": "Nivel",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordena niveles para mejor UX y agrega etiqueta de vacío
        self.fields["nivel"].queryset = Nivel.objects.order_by("nombre")
        self.fields["nivel"].empty_label = "— Seleccioná un nivel —"

        # Normaliza valores iniciales (si quisieras formatear, acá es el lugar)
        # No es estrictamente necesario porque Django ya los muestra correctos.

    # Normalización “suave”: string → None y money() para asegurar dos decimales
    def _normalize_money_or_none(self, value):
        if value in ("", None):
            return None
        return money(value)

    def clean_nombre(self):
        nombre = (self.cleaned_data.get("nombre") or "").strip()
        # Podés ajustar el casing si querés estandarizar
        # p.ej. nombre = nombre.upper()
        if not nombre:
            raise ValidationError("El nombre del curso no puede estar vacío.")
        return nombre

    def clean_monto_cuota_override(self):
        value = self.cleaned_data.get("monto_cuota_override")
        if value in ("", None):
            return None
        if value < 0:
            raise ValidationError("El monto no puede ser negativo.")
        return self._normalize_money_or_none(value)

    def clean_monto_inscripcion_override(self):
        value = self.cleaned_data.get("monto_inscripcion_override")
        if value in ("", None):
            return None
        if value < 0:
            raise ValidationError("El monto no puede ser negativo.")
        return self._normalize_money_or_none(value)

    def clean(self):
        data = super().clean()
        nivel = data.get("nivel")
        nombre = data.get("nombre")

        # Validación de unicidad a nivel formulario (evita esperar al error de DB)
        if nivel and nombre:
            exists = Curso.objects.filter(
                nivel=nivel,
                nombre__iexact=nombre
            ).exclude(pk=getattr(self.instance, "pk", None)).exists()
            if exists:
                self.add_error("nombre", "Ya existe un curso con ese nombre en este nivel.")

        return data


# ─────────────────────────────────────────────────────────
# Tarifas 
# ─────────────────────────────────────────────────────────
from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, Submit, HTML
from .models import TarifaNivel

class TarifaNivelForm(forms.ModelForm):
    class Meta:
        model = TarifaNivel
        fields = ["ciclo", "nivel", "monto_inscripcion", "monto_cuota_mensual"]
        widgets = {
            "ciclo": forms.Select(attrs={"class": "form-select"}),
            "nivel": forms.Select(attrs={"class": "form-select"}),
            "monto_inscripcion": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "monto_cuota_mensual": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column(Field("ciclo"), css_class="col-md-6"),
                Column(Field("nivel"), css_class="col-md-6"),
            ),
            Row(
                Column(Field("monto_inscripcion"), css_class="col-md-6"),
                Column(Field("monto_cuota_mensual"), css_class="col-md-6"),
            ),
            HTML('<div class="mt-3"></div>'),
            Submit("submit", "Guardar", css_class="btn btn-primary"),
        )

    def clean(self):
        cleaned = super().clean()
        ciclo = cleaned.get("ciclo")
        nivel = cleaned.get("nivel")
        if ciclo and nivel:
            qs = TarifaNivel.objects.filter(ciclo=ciclo, nivel=nivel)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Ya existe una tarifa para este Ciclo y Nivel.")
        return cleaned


from decimal import Decimal
from django import forms
from django.core.validators import MinValueValidator
from django.utils import timezone

from .models import Cuota

# ─────────────────────────────────────────────────────────
# Tarifas 
# ─────────────────────────────────────────────────────────

class CuotaCobroForm(forms.ModelForm):
    """
    Form para cobrar una cuota:
    - Permite elegir la fecha de pago (default: hoy)
    - Permite ajustar el descuento antes de cobrar (opcional)
    El recargo/total NO se ingresan: se calculan vía services.
    """
    fecha_pago = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date"}),
        initial=timezone.localdate,
        label="Fecha de pago"
    )

    # Si querés impedir que el cajero toque el descuento, poné disabled=True o eliminá este campo.
    descuento = forms.DecimalField(
        required=False,
        initial=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        decimal_places=2,
        max_digits=12,
        label="Descuento",
        help_text="Opcional. Se resta del importe base antes de evaluar recargo."
    )

    class Meta:
        model = Cuota
        fields = ["fecha_pago", "descuento"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si la cuota ya tiene un descuento precargado, mostrarlo
        if self.instance and getattr(self.instance, "descuento", None) is not None:
            self.fields["descuento"].initial = self.instance.descuento

    def clean(self):
        cleaned = super().clean()
        # reglas adicionales si necesitás…
        return cleaned
