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

    def clean_anio(self):
        anio = self.cleaned_data.get('anio')
        qs = CicloLectivo.objects.filter(anio=anio)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"El ciclo {anio} ya existe.")
        return anio

    def clean(self):
        cleaned_data = super().clean()
        anio = cleaned_data.get('anio')
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        # 1️⃣ Validar orden cronológico
        if fecha_inicio and fecha_fin and fecha_inicio >= fecha_fin:
            raise forms.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")

        # 2️⃣ Validar que las fechas pertenezcan al mismo año del ciclo
        if anio:
            if fecha_inicio and fecha_inicio.year != anio:
                self.add_error('fecha_inicio', f"La fecha de inicio debe ser del año {anio}.")
            if fecha_fin and fecha_fin.year != anio:
                self.add_error('fecha_fin', f"La fecha de fin debe ser del año {anio}.")

        return cleaned_data


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
            'fecha_vigencia_desde': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos editando, no requerimos la fecha
        if self.instance and self.instance.pk:
            self.fields['fecha_vigencia_desde'].required = False
            # 👇 Aseguramos que la fecha se muestre en formato HTML válido
            if self.instance.fecha_vigencia_desde:
                self.initial['fecha_vigencia_desde'] = self.instance.fecha_vigencia_desde.strftime('%Y-%m-%d')

    def clean(self):
        cleaned_data = super().clean()
        ciclo = cleaned_data.get('ciclo')
        nivel = cleaned_data.get('nivel')
        fecha_vigencia_desde = cleaned_data.get('fecha_vigencia_desde')
        nuevo_activo = cleaned_data.get('activo')

        # --- Crear: la fecha es obligatoria ---
        if not self.instance.pk and not fecha_vigencia_desde:
            raise forms.ValidationError("Debes ingresar la fecha de vigencia desde.")

        # --- Editar: mantener la fecha anterior si no se envía ---
        if self.instance.pk and not fecha_vigencia_desde:
            cleaned_data['fecha_vigencia_desde'] = self.instance.fecha_vigencia_desde
            fecha_vigencia_desde = self.instance.fecha_vigencia_desde

        # --- Validar duplicados activos ---
        if not self.instance.pk:
            if nuevo_activo:
                existe_activo = MontoNivel.objects.filter(
                    ciclo=ciclo, nivel=nivel, activo=True
                ).exists()
                if existe_activo:
                    raise forms.ValidationError(
                        "Ya existe un monto activo para este nivel en este ciclo."
                    )
        else:
            era_activo = bool(self.instance.activo)
            if not era_activo and nuevo_activo:
                existe_otro_activo = MontoNivel.objects.filter(
                    ciclo=ciclo, nivel=nivel, activo=True
                ).exclude(pk=self.instance.pk).exists()
                if existe_otro_activo:
                    raise forms.ValidationError(
                        "No se puede activar este monto porque ya existe otro monto activo."
                    )
                hay_sucesor = MontoNivel.objects.filter(
                    ciclo=ciclo,
                    nivel=nivel,
                    fecha_vigencia_desde__gt=self.instance.fecha_vigencia_desde
                ).exists()
                if hay_sucesor:
                    raise forms.ValidationError(
                        "No se puede volver a activar un monto anterior, ya existe un monto posterior."
                    )

        # --- 🚫 Validar coherencia temporal (creación y edición) ---
        if fecha_vigencia_desde:
            # Buscar montos del mismo ciclo/nivel con fechas iguales o posteriores
            conflicto = MontoNivel.objects.filter(
                ciclo=ciclo,
                nivel=nivel,
                fecha_vigencia_desde=fecha_vigencia_desde
            ).exclude(pk=self.instance.pk).first()

            if conflicto:
                raise forms.ValidationError(
                    f"Ya existe otro monto con la misma fecha de vigencia ({conflicto.fecha_vigencia_desde.strftime('%d/%m/%Y')})."
                )

            # Si es creación, la fecha debe ser posterior a la última
            if not self.instance.pk:
                ultimo_monto = (
                    MontoNivel.objects.filter(ciclo=ciclo, nivel=nivel)
                    .exclude(pk=self.instance.pk)
                    .order_by('-fecha_vigencia_desde')
                    .first()
                )
                if ultimo_monto and fecha_vigencia_desde <= ultimo_monto.fecha_vigencia_desde:
                    raise forms.ValidationError(
                        f"La fecha de vigencia debe ser posterior a la última establecida "
                        f"({ultimo_monto.fecha_vigencia_desde.strftime('%d/%m/%Y')})."
                    )
            else:
                # Si es edición, asegurar que no sea anterior a ningún monto del mismo ciclo/nivel
                anterior = MontoNivel.objects.filter(
                    ciclo=ciclo,
                    nivel=nivel,
                    fecha_vigencia_desde__lt=fecha_vigencia_desde
                ).exclude(pk=self.instance.pk).order_by('-fecha_vigencia_desde').first()
                posterior = MontoNivel.objects.filter(
                    ciclo=ciclo,
                    nivel=nivel,
                    fecha_vigencia_desde__gt=fecha_vigencia_desde
                ).exclude(pk=self.instance.pk).order_by('fecha_vigencia_desde').first()

                if anterior and fecha_vigencia_desde <= anterior.fecha_vigencia_desde:
                    raise forms.ValidationError(
                        f"La fecha de vigencia no puede ser anterior o igual a la de otro monto del mismo nivel "
                        f"({anterior.fecha_vigencia_desde.strftime('%d/%m/%Y')})."
                    )

                if posterior and fecha_vigencia_desde >= posterior.fecha_vigencia_desde:
                    raise forms.ValidationError(
                        f"La fecha de vigencia no puede ser igual o posterior a la del siguiente monto "
                        f"({posterior.fecha_vigencia_desde.strftime('%d/%m/%Y')})."
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

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        # Excluir el registro actual en caso de edición
        qs = Beca.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe una beca con ese nombre.")
        return nombre
