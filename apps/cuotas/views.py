from datetime import datetime
from django.contrib import messages
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView

from .models import (
    CicloLectivo, Nivel, Curso, TarifaNivel,
    VencimientoMensual, Beneficio, BeneficioInscripcion,
    Inscripcion, Cuota
)
from .forms import (
    CicloLectivoForm, NivelForm, CursoForm, TarifaNivelForm,
    VencimientoMensualForm, BeneficioForm, BeneficioInscripcionForm,
    InscripcionForm, CuotaCobroForm
)
from .services import generar_cuotas_para_inscripcion

from .services import generar_cuotas_para_inscripcion, generar_cuotas_masivo

# ==========================
# Home de la app
# ==========================
def cuotas_home(request):
    return render(request, "cuotas/home.html", {})


# ==========================
# Base genéricas
# ==========================
class BaseList(ListView):
    paginate_by = 20
    template_name = "cuotas/generic_list.html"
    context_object_name = "object_list"


class BaseCreate(CreateView):
    template_name = "cuotas/generic_form.html"
    success_url = reverse_lazy("cuotas:ciclo_list")  # se sobrescribe en cada view
    success_message = "Creado correctamente."

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class BaseUpdate(UpdateView):
    template_name = "cuotas/generic_form.html"
    success_url = reverse_lazy("cuotas:ciclo_list")
    success_message = "Actualizado correctamente."

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

# ==========================
# CICLOS LECTIVOS
# ==========================
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import CicloLectivo
from .forms import CicloLectivoForm
from .base import BaseList, BaseCreate, BaseUpdate  # tus vistas genéricas

# 🔹 Listado de ciclos
class CicloListView(BaseList):
    model = CicloLectivo
    template_name = "cuotas/ciclo_lectivo_list.html"
    context_object_name = "ciclos"
    ordering = ["-anio"]

# 🔹 Crear nuevo ciclo
class CicloCreateView(BaseCreate):
    form_class = CicloLectivoForm
    success_url = reverse_lazy("cuotas:ciclo_list")
    template_name = "cuotas/ciclo_lectivo_form.html"

    def form_valid(self, form):
        ciclo = form.save(commit=False)
        # Si es el primer ciclo, lo marcamos como activo
        if not CicloLectivo.objects.exists():
            ciclo.activo = True
        ciclo.save()
        messages.success(self.request, f"Ciclo {ciclo.anio} creado correctamente.")
        return redirect(self.success_url)

# 🔹 Editar ciclo existente
class CicloUpdateView(BaseUpdate):
    model = CicloLectivo
    form_class = CicloLectivoForm
    success_url = reverse_lazy("cuotas:ciclo_list")
    template_name = "cuotas/ciclo_lectivo_form.html"

# 🔹 Activar un ciclo (desactiva los demás)
def activar_ciclo(request, ciclo_id):
    ciclo = get_object_or_404(CicloLectivo, pk=ciclo_id)
    ciclo.activo = True
    ciclo.save()  # la lógica del modelo desactiva los demás
    messages.success(request, f"✅ Ciclo {ciclo.anio} activado correctamente.")
    return redirect("cuotas:ciclo_list")


# ==========================
# Niveles
# ==========================
class NivelListView(BaseList):
    model = Nivel


class NivelCreateView(BaseCreate):
    form_class = NivelForm
    success_url = reverse_lazy("cuotas:nivel_list")


class NivelUpdateView(BaseUpdate):
    model = Nivel
    form_class = NivelForm
    success_url = reverse_lazy("cuotas:nivel_list")


# ==========================
# Cursos
# ==========================
class CursoListView(BaseList):
    model = Curso
    queryset = Curso.objects.select_related("nivel")


class CursoCreateView(BaseCreate):
    form_class = CursoForm
    success_url = reverse_lazy("cuotas:curso_list")


class CursoUpdateView(BaseUpdate):
    model = Curso
    form_class = CursoForm
    success_url = reverse_lazy("cuotas:curso_list")


# ==========================
# Tarifas por nivel
# ==========================
class TarifaListView(BaseList):
    model = TarifaNivel
    queryset = TarifaNivel.objects.select_related("ciclo", "nivel")


class TarifaCreateView(BaseCreate):
    form_class = TarifaNivelForm
    success_url = reverse_lazy("cuotas:tarifa_list")


class TarifaUpdateView(BaseUpdate):
    model = TarifaNivel
    form_class = TarifaNivelForm
    success_url = reverse_lazy("cuotas:tarifa_list")


# ==========================
# Vencimientos
# ==========================
class VencimientoListView(BaseList):
    model = VencimientoMensual
    queryset = VencimientoMensual.objects.select_related("ciclo")


class VencimientoCreateView(BaseCreate):
    form_class = VencimientoMensualForm
    success_url = reverse_lazy("cuotas:vencimiento_list")


class VencimientoUpdateView(BaseUpdate):
    model = VencimientoMensual
    form_class = VencimientoMensualForm
    success_url = reverse_lazy("cuotas:vencimiento_list")


# ==========================
# Beneficios
# ==========================
class BeneficioListView(BaseList):
    model = Beneficio


class BeneficioCreateView(BaseCreate):
    form_class = BeneficioForm
    success_url = reverse_lazy("cuotas:beneficio_list")


class BeneficioUpdateView(BaseUpdate):
    model = Beneficio
    form_class = BeneficioForm
    success_url = reverse_lazy("cuotas:beneficio_list")


# ==========================
# Beneficios por inscripción
# ==========================
class BeneficioInscripcionListView(BaseList):
    model = BeneficioInscripcion
    queryset = BeneficioInscripcion.objects.select_related("inscripcion", "beneficio")


class BeneficioInscripcionCreateView(BaseCreate):
    form_class = BeneficioInscripcionForm
    success_url = reverse_lazy("cuotas:beneficio_insc_list")


class BeneficioInscripcionUpdateView(BaseUpdate):
    model = BeneficioInscripcion
    form_class = BeneficioInscripcionForm
    success_url = reverse_lazy("cuotas:beneficio_insc_list")


# ==========================
# Inscripciones
# ==========================
class InscripcionListView(BaseList):
    model = Inscripcion
    queryset = (
        Inscripcion.objects
        .select_related("estudiante", "ciclo", "nivel", "curso")
        .order_by("-ciclo__anio", "estudiante__apellidos_estudiante")
    )


class InscripcionCreateView(BaseCreate):
    form_class = InscripcionForm
    success_url = reverse_lazy("cuotas:inscripcion_list")


class InscripcionUpdateView(BaseUpdate):
    model = Inscripcion
    form_class = InscripcionForm
    success_url = reverse_lazy("cuotas:inscripcion_list")


def generar_cuotas_view(request, pk):
    inscripcion = get_object_or_404(
        Inscripcion.objects.select_related("ciclo", "nivel", "curso"),
        pk=pk
    )
    ids = generar_cuotas_para_inscripcion(inscripcion)
    if ids:
        messages.success(request, f"Se generaron {len(ids)} cuotas.")
    else:
        messages.info(request, "No se generaron cuotas (ya existían).")
    return redirect("cuotas:inscripcion_cuotas", pk=inscripcion.pk)


def cuotas_por_inscripcion(request, pk):
    inscripcion = get_object_or_404(
        Inscripcion.objects.select_related("estudiante", "ciclo", "nivel", "curso"),
        pk=pk
    )
    cuotas = (
        Cuota.objects.filter(inscripcion=inscripcion)
        .order_by("mes")
        .prefetch_related("pagos")
    )
    return render(request, "cuotas/inscripcion_cuotas.html", {
        "inscripcion": inscripcion,
        "cuotas": cuotas
    })


# ==========================
# Cobro de Cuota
# ==========================
def cobrar_cuota(request, cuota_id):
    cuota = get_object_or_404(
        Cuota.objects.select_related(
            "inscripcion",
            "inscripcion__ciclo",
            "inscripcion__estudiante",
            "inscripcion__nivel",
            "inscripcion__curso",
        ),
        pk=cuota_id
    )

    if request.method == "POST":
        form = CuotaCobroForm(request.POST)
        if form.is_valid():
            medio = form.cleaned_data["medio_pago"]
            monto_cobrado = form.cleaned_data["monto_cobrado"]
            fecha_pago_dt = form.cleaned_data["fecha_pago"]

            # Recalcula con la fecha ingresada y marca pagada
            cuota.marcar_pagada(fecha_pago_dt=fecha_pago_dt, monto_cobrado=monto_cobrado)
            cuota.save()

            # Registra pago
            from .models import Pago
            Pago.objects.create(
                cuota=cuota,
                monto_pagado=monto_cobrado,
                medio_pago=medio,
            )

            messages.success(
                request,
                f"Cuota del mes {cuota.mes} cobrada. Total calculado: ${cuota.total_a_pagar}"
            )
            return redirect("cuotas:inscripcion_cuotas", pk=cuota.inscripcion.pk)
    else:
        form = CuotaCobroForm(
            initial={"monto_cobrado": cuota.total_a_pagar}
        )

    # Vista de cobro con formulario + preview (AJAX aparte)
    return render(request, "cuotas/cobrar_cuota.html", {
        "cuota": cuota,
        "form": form
    })


# ==========================
# API AJAX: previsualización de total según fecha
# ==========================
def preview_total_cuota(request, cuota_id):
    cuota = get_object_or_404(Cuota, pk=cuota_id)
    # fecha en querystring: ?ts=2026-03-11T10:00
    ts = request.GET.get("ts")
    try:
        fecha_dt = datetime.fromisoformat(ts) if ts else None
    except ValueError:
        return JsonResponse({"ok": False, "error": "Fecha inválida"}, status=400)

    # Recalcula en memoria (no guarda)
    cuota.recalcular(fecha_pago_dt=fecha_dt)
    return JsonResponse({
        "ok": True,
        "monto_base": str(cuota.monto_base),
        "descuentos": str(cuota.monto_descuentos),
        "recargos": str(cuota.monto_recargos),
        "total": str(cuota.total_a_pagar),
    })



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django import forms
from .models import CicloLectivo

class CicloLectivoForm(forms.ModelForm):
    class Meta:
        model = CicloLectivo
        fields = ["anio", "fecha_inicio", "fecha_fin"]

def ciclo_lectivo_list(request):
    ciclos = CicloLectivo.objects.all().order_by("-anio")

    if request.method == "POST":
        form = CicloLectivoForm(request.POST)
        if form.is_valid():
            ciclo = form.save(commit=False)
            # Si es el primero, lo marcamos activo automáticamente
            if not CicloLectivo.objects.exists():
                ciclo.activo = True
            ciclo.save()
            messages.success(request, f"Ciclo {ciclo.anio} creado correctamente.")
            return redirect("cuotas:ciclos")
    else:
        form = CicloLectivoForm()

    return render(request, "cuotas/ciclo_lectivo_list.html", {"ciclos": ciclos, "form": form})

def activar_ciclo(request, ciclo_id):
    ciclo = get_object_or_404(CicloLectivo, pk=ciclo_id)
    ciclo.activo = True
    ciclo.save()  # esto desactiva los demás (por la lógica en el modelo)
    messages.success(request, f"Ciclo {ciclo.anio} activado correctamente.")
    return redirect("cuotas:ciclos")
