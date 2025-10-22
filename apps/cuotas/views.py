
# apps/cuotas/views_tarifas.py
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView, UpdateView, DeleteView

from .models import TarifaNivel
from .forms import TarifaNivelForm
from datetime import datetime
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
from .models import CicloLectivo
from .forms import CicloLectivoForm

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



from django.shortcuts import render, redirect, get_object_or_404
from .models import CicloLectivo
from .forms import CicloLectivoForm

def ciclos_list(request):
    form = CicloLectivoForm()
    ciclos = CicloLectivo.objects.order_by('-anio')
    activo = CicloLectivo.objects.filter(activo=True).first()
    return render(request, 'cuotas/ciclo_lectivo_list.html', {  # <-- acá
        'form': form,
        'ciclos': ciclos,
        'CUOTAS_CICLO_ACTIVO': activo,
    })

def ciclo_create(request):
    if request.method != 'POST':
        return redirect('cuotas:ciclo_list')
    form = CicloLectivoForm(request.POST)
    if form.is_valid():
        ciclo = form.save(commit=False)
        if not CicloLectivo.objects.exists():
            ciclo.activo = True
        ciclo.save()
        messages.success(request, f"Ciclo {ciclo.anio} creado correctamente.")
        return redirect('cuotas:ciclo_list')

    # Si hay errores, re-render al MISMO template
    ciclos = CicloLectivo.objects.order_by('-anio')
    activo = CicloLectivo.objects.filter(activo=True).first()
    return render(request, 'cuotas/ciclo_lectivo_list.html', {  # <-- acá
        'form': form,
        'ciclos': ciclos,
        'CUOTAS_CICLO_ACTIVO': activo,
    })


from django.shortcuts import get_object_or_404, redirect
from .models import CicloLectivo

def activar_ciclo(request, pk):
    ciclo = get_object_or_404(CicloLectivo, pk=pk)
    ciclo.activo = True
    ciclo.save()  # el save() desactiva los otros
    messages.success(request, f"Ciclo {ciclo.anio} activado correctamente.")
    return redirect('cuotas:ciclo_list')          # ✅ coincide con urls

# ==========================
# Niveles
# ==========================
class NivelListView(BaseList):
    model = Nivel
    template_name = "cuotas/nivel_list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nombre__icontains=q.strip())
        return qs


class NivelCreateView(BaseCreate):
    form_class = NivelForm
    template_name = "cuotas/nivel_form.html"
    success_url = reverse_lazy("cuotas:nivel_list")


class NivelUpdateView(BaseUpdate):
    model = Nivel
    form_class = NivelForm
    template_name = "cuotas/nivel_form.html"
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
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import TarifaNivel
from .forms import TarifaNivelForm

class TarifaNivelListView(LoginRequiredMixin, ListView):
    model = TarifaNivel
    template_name = "cuotas/tarifa_nivel_list.html"
    context_object_name = "tarifas"
    paginate_by = 20

    def get_queryset(self):
        qs = (
            TarifaNivel.objects
            .select_related("ciclo", "nivel")
            .order_by("ciclo", "nivel")
        )
        # Filtros GET: ?ciclo=<id>&nivel=<id>&q=<texto>
        ciclo_id = self.request.GET.get("ciclo")
        nivel_id = self.request.GET.get("nivel")
        q = (self.request.GET.get("q") or "").strip()

        if ciclo_id:
            qs = qs.filter(ciclo_id=ciclo_id)
        if nivel_id:
            qs = qs.filter(nivel_id=nivel_id)
        if q:
            qs = qs.filter(
                Q(nivel__nombre__icontains=q) |
                Q(ciclo__anio__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["f_ciclo"] = self.request.GET.get("ciclo", "")
        ctx["f_nivel"] = self.request.GET.get("nivel", "")
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class TarifaNivelCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = TarifaNivel
    form_class = TarifaNivelForm
    template_name = "cuotas/tarifa_nivel_form.html"
    success_url = reverse_lazy("cuotas:tarifa_nivel_list")
    success_message = "Tarifa creada correctamente."

    def form_invalid(self, form):
        messages.error(self.request, "Revisá los campos marcados.")
        return super().form_invalid(form)


class TarifaNivelUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = TarifaNivel
    form_class = TarifaNivelForm
    template_name = "cuotas/tarifa_nivel_form.html"
    success_url = reverse_lazy("cuotas:tarifa_nivel_list")
    success_message = "Tarifa actualizada correctamente."

    def form_invalid(self, form):
        messages.error(self.request, "Revisá los campos marcados.")
        return super().form_invalid(form)


class TarifaNivelDeleteView(LoginRequiredMixin, DeleteView):
    model = TarifaNivel
    template_name = "cuotas/tarifa_nivel_confirm_delete.html"
    success_url = reverse_lazy("cuotas:tarifa_nivel_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Tarifa eliminada correctamente.")
        return super().delete(request, *args, **kwargs)




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

from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Curso, Nivel
from .forms import CursoForm


# ─────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────
def _qs_filtrado(request):
    """
    Aplica filtros de querystring:
      - q: busca por nombre del curso y nombre del nivel
      - nivel: id del nivel
    """
    qs = Curso.objects.select_related("nivel").all()

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(nombre__icontains=q) |
            Q(nivel__nombre__icontains=q)
        )

    nivel_id = request.GET.get("nivel")
    if nivel_id:
        qs = qs.filter(nivel_id=nivel_id)

    # El ordenamiento por defecto ya lo define el Meta.ordering del modelo.
    return qs


# ─────────────────────────────────────────────────────────
# Listado
# ─────────────────────────────────────────────────────────
class CursoListView(ListView):
    model = Curso
    template_name = "cuotas/curso_list.html"
    context_object_name = "cursos"
    paginate_by = 20  # ajustá a gusto

    def get_queryset(self):
        return _qs_filtrado(self.request)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["niveles"] = Nivel.objects.order_by("nombre")
        ctx["nivel_seleccionado"] = self.request.GET.get("nivel") or ""
        ctx["q"] = self.request.GET.get("q") or ""
        ctx["total"] = self.get_queryset().count()
        return ctx


# ─────────────────────────────────────────────────────────
# Mixins para Create/Update con manejo de IntegrityError
# ─────────────────────────────────────────────────────────
class CursoBaseEditMixin(SuccessMessageMixin):
    model = Curso
    form_class = CursoForm
    template_name = "cuotas/curso_form.html"
    success_url = reverse_lazy("cuotas:curso_list")
    success_message = "Curso guardado correctamente."

    def form_valid(self, form):
        """
        Protegemos el guardado ante posibles carreras de escritura que violen
        unique_together (nivel + nombre), devolviendo un error amigable.
        """
        try:
            with transaction.atomic():
                return super().form_valid(form)
        except IntegrityError:
            form.add_error("nombre", "Ya existe un curso con ese nombre en este nivel.")
            # No usamos messages acá para que quede asociado al campo
            return self.form_invalid(form)


# ─────────────────────────────────────────────────────────
# Crear
# ─────────────────────────────────────────────────────────
class CursoCreateView(CursoBaseEditMixin, CreateView):
    # success_message ya definido en mixin
    pass


# ─────────────────────────────────────────────────────────
# Editar
# ─────────────────────────────────────────────────────────
class CursoUpdateView(CursoBaseEditMixin, UpdateView):
    success_message = "Curso actualizado correctamente."


# ─────────────────────────────────────────────────────────
# Eliminar
# ─────────────────────────────────────────────────────────
class CursoDeleteView(DeleteView):
    model = Curso
    template_name = "cuotas/curso_confirm_delete.html"
    success_url = reverse_lazy("cuotas:curso_list")

    def delete(self, request, *args, **kwargs):
        """
        Si no se puede borrar por integridad referencial (por ejemplo, Inscripciones
        que referencian este Curso), mostramos un mensaje y redirigimos.
        """
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(request, "Curso eliminado correctamente.")
            return response
        except IntegrityError:
            messages.error(
                request,
                "No se puede eliminar el curso porque está en uso (tiene relaciones asociadas)."
            )
            return redirect(self.success_url)


# ─────────────────────────────────────────────────────────
# (Opcional) Endpoint JSON para selects dependientes
#   GET /cuotas/api/cursos?nivel=<id>
# ─────────────────────────────────────────────────────────
def cursos_por_nivel_api(request):
    nivel_id = request.GET.get("nivel")
    qs = Curso.objects.select_related("nivel")
    if nivel_id:
        qs = qs.filter(nivel_id=nivel_id)
    data = [
        {"id": c.id, "nombre": c.nombre, "nivel": c.nivel.nombre}
        for c in qs.order_by("nombre")
    ]
    return JsonResponse({"results": data})



# ─────────────────────────────────────────────────────────
#  Views de Tarifas 
#  
# ─────────────────────────────────────────────────────────
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import TarifaNivel
from .forms import TarifaNivelForm

class TarifaNivelListView(LoginRequiredMixin, ListView):
    model = TarifaNivel
    template_name = "cuotas/tarifa_nivel_list.html"   # ✅ correcto
    context_object_name = "tarifas"
    paginate_by = 20

    def get_queryset(self):
        qs = (
            TarifaNivel.objects
            .select_related("ciclo", "nivel")
            .order_by("ciclo", "nivel")
        )
        # Filtros simples por GET ?ciclo= &nivel=
        ciclo_id = self.request.GET.get("ciclo")
        nivel_id = self.request.GET.get("nivel")
        search = self.request.GET.get("q")

        if ciclo_id:
            qs = qs.filter(ciclo_id=ciclo_id)
        if nivel_id:
            qs = qs.filter(nivel_id=nivel_id)
        if search:
            qs = qs.filter(
                Q(ciclo__id__icontains=search) |
                Q(nivel__nombre__icontains=search)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Pasá los valores actuales para mantener filtros en la UI
        ctx["f_ciclo"] = self.request.GET.get("ciclo", "")
        ctx["f_nivel"] = self.request.GET.get("nivel", "")
        ctx["q"] = self.request.GET.get("q", "")
        return ctx



class TarifaNivelCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = TarifaNivel
    form_class = TarifaNivelForm
    template_name = "cuotas/tarifa_nivel_form.html"
    success_url = reverse_lazy("cuotas:tarifa_nivel_list")
    success_message = "Tarifa creada correctamente."

    def form_invalid(self, form):
        messages.error(self.request, "Revisá los campos marcados.")
        return super().form_invalid(form)


class TarifaNivelUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = TarifaNivel
    form_class = TarifaNivelForm
    template_name = "cuotas/tarifa_nivel_form.html"
    success_url = reverse_lazy("cuotas:tarifa_nivel_list")
    success_message = "Tarifa actualizada correctamente."

    def form_invalid(self, form):
        messages.error(self.request, "Revisá los campos marcados.")
        return super().form_invalid(form)


class TarifaNivelDeleteView(LoginRequiredMixin, DeleteView):
    model = TarifaNivel
    template_name = "cuotas/tarifa_nivel_confirm_delete.html"
    success_url = reverse_lazy("cuotas:tarifa_nivel_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Tarifa eliminada correctamente.")
        return super().delete(request, *args, **kwargs)



from datetime import date
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone

from .models import Inscripcion, Cuota
from .forms import CuotaCobroForm
from .services import calcular_importe_con_recargo, aplicar_cobro_a_cuota


# ================
# Listado de cuotas por inscripción
# ================
def cuota_list(request, inscripcion_id):
    """
    Muestra todas las cuotas de una inscripción (12 meses típicamente),
    con estado y acciones.
    """
    inscripcion = get_object_or_404(
        Inscripcion.objects.select_related("ciclo", "nivel", "curso"),
        pk=inscripcion_id
    )
    cuotas = (
        Cuota.objects
        .filter(inscripcion=inscripcion)
        .order_by("mes")
    )

    context = {
        "inscripcion": inscripcion,
        "cuotas": cuotas,
    }
    return render(request, "cuotas/cuota_list.html", context)


# ================
# Cobrar una cuota
# ================
def cuota_cobrar(request, cuota_id):
    """
    GET: Muestra form con fecha_pago (+opcional descuento) y una simulación del cálculo.
    POST: Aplica el cobro (services.aplicar_cobro_a_cuota), actualizando descuento si corresponde.
    """
    cuota = get_object_or_404(
        Cuota.objects.select_related("inscripcion", "inscripcion__ciclo", "inscripcion__nivel"),
        pk=cuota_id
    )

    if getattr(cuota, "pagado", False):
        messages.info(request, "Esta cuota ya está marcada como pagada.")
        return redirect(reverse("cuotas:cuota_list", args=[cuota.inscripcion_id]))

    if request.method == "POST":
        form = CuotaCobroForm(request.POST, instance=cuota)
        if form.is_valid():
            # Persistimos el descuento editado antes de calcular
            descuento = form.cleaned_data.get("descuento")
            if descuento is not None:
                cuota.descuento = descuento
                cuota.save(update_fields=["descuento"])

            fecha_pago = form.cleaned_data.get("fecha_pago") or timezone.localdate()

            # Cobro real (calcula recargo/total y marca pagada)
            datos = aplicar_cobro_a_cuota(cuota_id=cuota.id, fecha_pago=fecha_pago)

            messages.success(
                request,
                (
                    f"✔ Cobro registrado. Cuota mes {datos['mes']:02d} | "
                    f"Corte: {datos['fecha_corte']:%d/%m/%Y} | "
                    f"Recargo: {datos['porcentaje']}% → ${datos['recargo']} | "
                    f"Total pagado: ${datos['total']} | Fecha pago: {datos['fecha_pago']:%d/%m/%Y}"
                )
            )
            return redirect(reverse("cuotas:cuota_list", args=[cuota.inscripcion_id]))
    else:
        form = CuotaCobroForm(instance=cuota)

    # ---- Simulación para mostrar en el GET (previa al cobro) ----
    fecha_simulada = form.initial.get("fecha_pago") or timezone.localdate()
    base_neta = (cuota.importe_base or 0) - (cuota.descuento or 0)
    if base_neta < 0:
        base_neta = 0

    sim = calcular_importe_con_recargo(
        ciclo=cuota.inscripcion.ciclo,
        mes=cuota.mes,
        importe_base=base_neta,
        fecha_pago=fecha_simulada,
    )

    context = {
        "cuota": cuota,
        "form": form,
        "sim": sim,                # dict con porcentaje, fecha_corte, aplica_recargo, recargo, total
        "base_neta": base_neta,    # para mostrar desglose
    }
    return render(request, "cuotas/cuota_cobrar.html", context)

class BaseList(ListView):
    paginate_by = 20
    template_name = "cuotas/generic_list.html"
    context_object_name = "object_list"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if getattr(self, "model", None):
            model = self.model
        else:
            qs = ctx.get("object_list")
            model = qs.model if qs is not None else None

        if model is not None:
            ctx["mname"] = model._meta.model_name                 # ej. "beneficio"
            ctx["mverbose"] = model._meta.verbose_name_plural     # ej. "Beneficios"
            ctx["mverbose_singular"] = model._meta.verbose_name   # ej. "Beneficio"
            ctx["app_label"] = model._meta.app_label              # ej. "cuotas"
        return ctx


# ==========================
# Vencimientos
# ==========================
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError, transaction, models
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from .models import VencimientoMensual
from .forms import VencimientoMensualForm


class VencimientoListView(ListView):
    model = VencimientoMensual
    template_name = "cuotas/vencimientos.html"
    context_object_name = "vencimientos"
    paginate_by = 20

    def get_queryset(self):
        qs = (
            VencimientoMensual.objects
            .select_related("ciclo")
            .order_by("-ciclo__anio", "mes")
        )
        q = (self.request.GET.get("q") or "").strip()
        if q:
            # Permite buscar por año (ej: 2025) o por mes "03"/"3"
            qs = qs.filter(
                models.Q(ciclo__anio__icontains=q) |
                models.Q(mes__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class VencimientoCreateView(SuccessMessageMixin, CreateView):
    model = VencimientoMensual
    form_class = VencimientoMensualForm
    template_name = "cuotas/vencimiento_form.html"
    success_url = reverse_lazy("cuotas:vencimiento_list")
    success_message = "Vencimiento creado correctamente."

    def form_valid(self, form):
        try:
            with transaction.atomic():
                return super().form_valid(form)
        except IntegrityError:
            form.add_error("mes", "Ya existe un vencimiento configurado para ese ciclo y mes.")
            messages.error(self.request, "Revisá los campos marcados.")
            return self.form_invalid(form)


class VencimientoUpdateView(SuccessMessageMixin, UpdateView):
    model = VencimientoMensual
    form_class = VencimientoMensualForm
    template_name = "cuotas/vencimiento_form.html"
    success_url = reverse_lazy("cuotas:vencimiento_list")
    success_message = "Vencimiento actualizado correctamente."

    def form_valid(self, form):
        try:
            with transaction.atomic():
                return super().form_valid(form)
        except IntegrityError:
            form.add_error("mes", "Ya existe un vencimiento configurado para ese ciclo y mes.")
            messages.error(self.request, "Revisá los campos marcados.")
            return self.form_invalid(form)



from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Beneficio, BeneficioInscripcion, Inscripcion
from .forms import BeneficioForm, BeneficioInscripcionForm

# ==========================
# Beneficio (CRUD)
# ==========================
class BeneficioListView(LoginRequiredMixin, ListView):
    model = Beneficio
    template_name = "cuotas/beneficio_list.html"
    context_object_name = "beneficios"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nombre__icontains=q)
        estado = self.request.GET.get("estado")
        if estado in {"activos", "inactivos"}:
            qs = qs.filter(activo=(estado == "activos"))
        return qs

class BeneficioCreateView(LoginRequiredMixin, CreateView):
    model = Beneficio
    form_class = BeneficioForm
    template_name = "cuotas/beneficio_form.html"
    success_url = reverse_lazy("cuotas:beneficio_list")

    def form_valid(self, form):
        messages.success(self.request, "Beneficio creado correctamente.")
        return super().form_valid(form)

class BeneficioUpdateView(LoginRequiredMixin, UpdateView):
    model = Beneficio
    form_class = BeneficioForm
    template_name = "cuotas/beneficio_form.html"
    success_url = reverse_lazy("cuotas:beneficio_list")

    def form_valid(self, form):
        messages.success(self.request, "Beneficio actualizado correctamente.")
        return super().form_valid(form)

class BeneficioDeleteView(LoginRequiredMixin, DeleteView):
    model = Beneficio
    template_name = "cuotas/beneficio_confirm_delete.html"
    success_url = reverse_lazy("cuotas:beneficio_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Beneficio eliminado correctamente.")
        return super().delete(request, *args, **kwargs)


# ==========================
# BeneficioInscripcion (CRUD)
# ==========================
class BeneficioInscripcionListView(LoginRequiredMixin, ListView):
    model = BeneficioInscripcion
    template_name = "cuotas/beneficioinscripcion_list.html"
    context_object_name = "asignaciones"
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related("inscripcion", "beneficio")
        inscripcion_id = self.kwargs.get("inscripcion_id")
        if inscripcion_id:
            qs = qs.filter(inscripcion_id=inscripcion_id)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        inscripcion_id = self.kwargs.get("inscripcion_id")
        ctx["inscripcion"] = None
        if inscripcion_id:
            ctx["inscripcion"] = get_object_or_404(Inscripcion, pk=inscripcion_id)
        return ctx

class BeneficioInscripcionCreateView(LoginRequiredMixin, CreateView):
    model = BeneficioInscripcion
    form_class = BeneficioInscripcionForm
    template_name = "cuotas/beneficioinscripcion_form.html"

    def get_initial(self):
        initial = super().get_initial()
        inscripcion_id = self.kwargs.get("inscripcion_id")
        if inscripcion_id:
            initial["inscripcion"] = get_object_or_404(Inscripcion, pk=inscripcion_id)
        return initial

    def get_success_url(self):
        inscripcion_id = self.kwargs.get("inscripcion_id")
        if inscripcion_id:
            messages.success(self.request, "Beneficio asignado correctamente.")
            return reverse_lazy("cuotas:beneficioinscripcion_list_by_inscripcion", kwargs={"inscripcion_id": inscripcion_id})
        messages.success(self.request, "Beneficio asignado correctamente.")
        return reverse_lazy("cuotas:beneficioinscripcion_list")

class BeneficioInscripcionUpdateView(LoginRequiredMixin, UpdateView):
    model = BeneficioInscripcion
    form_class = BeneficioInscripcionForm
    template_name = "cuotas/beneficioinscripcion_form.html"

    def get_success_url(self):
        asignacion = self.object
        messages.success(self.request, "Asignación actualizada correctamente.")
        return reverse_lazy("cuotas:beneficioinscripcion_list_by_inscripcion", kwargs={"inscripcion_id": asignacion.inscripcion_id})

class BeneficioInscripcionDeleteView(LoginRequiredMixin, DeleteView):
    model = BeneficioInscripcion
    template_name = "cuotas/beneficioinscripcion_confirm_delete.html"

    def get_success_url(self):
        asignacion = self.get_object()
        messages.success(self.request, "Asignación eliminada correctamente.")
        return reverse_lazy("cuotas:beneficioinscripcion_list_by_inscripcion", kwargs={"inscripcion_id": asignacion.inscripcion_id})
    

    



from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from .models import Inscripcion, Cuota
from .forms import InscripcionForm, CuotaForm

# Intentamos usar tu service si existe
try:
    from .services import generar_cuotas_para_inscripcion as _generar_cuotas_service
except Exception:
    _generar_cuotas_service = None


def _fallback_generar_cuotas(inscripcion: Inscripcion):
    """Genera 12 cuotas simples sin beneficios ni recargos."""
    # Evitar duplicados si ya existen
    if inscripcion.cuotas.exists():
        return
    for mes in range(1, 13):
        monto_base = inscripcion.get_monto_base_cuota()
        Cuota.objects.create(
            inscripcion=inscripcion,
            mes=mes,
            monto_base=monto_base,
            monto_descuentos=Decimal("0.00"),
            monto_recargos=Decimal("0.00"),
            total_a_pagar=monto_base,
        )


# ==========================
# Inscripciones
# ==========================
class InscripcionListView(LoginRequiredMixin, ListView):
    model = Inscripcion
    template_name = "cuotas/inscripcion_list.html"
    context_object_name = "inscripciones"
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related("estudiante", "ciclo", "nivel", "curso")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(estudiante__apellidos_estudiante__icontains=q) | qs.filter(estudiante__nombres_estudiante__icontains=q) | qs.filter(estudiante__dni_estudiante__icontains=q)
        ciclo_id = self.request.GET.get("ciclo")
        if ciclo_id:
            qs = qs.filter(ciclo_id=ciclo_id)
        nivel_id = self.request.GET.get("nivel")
        if nivel_id:
            qs = qs.filter(nivel_id=nivel_id)
        curso_id = self.request.GET.get("curso")
        if curso_id:
            qs = qs.filter(curso_id=curso_id)
        return qs


class InscripcionCreateView(LoginRequiredMixin, CreateView):
    model = Inscripcion
    form_class = InscripcionForm
    template_name = "cuotas/inscripcion_form.html"
    success_url = reverse_lazy("cuotas:inscripcion_list")

    def form_valid(self, form):
        # Si no viene monto, usar helper del modelo
        insc: Inscripcion = form.save(commit=False)
        if not insc.monto_inscripcion or insc.monto_inscripcion == 0:
            insc.monto_inscripcion = insc.get_monto_base_inscripcion()
        insc.save()

        # Generar cuotas
        if _generar_cuotas_service:
            _generar_cuotas_service(insc)
        else:
            _fallback_generar_cuotas(insc)

        messages.success(self.request, "Inscripción creada y cuotas generadas correctamente.")
        return super().form_valid(form)


class InscripcionUpdateView(LoginRequiredMixin, UpdateView):
    model = Inscripcion
    form_class = InscripcionForm
    template_name = "cuotas/inscripcion_form.html"
    success_url = reverse_lazy("cuotas:inscripcion_list")

    def form_valid(self, form):
        messages.success(self.request, "Inscripción actualizada correctamente.")
        return super().form_valid(form)


class InscripcionDeleteView(LoginRequiredMixin, DeleteView):
    model = Inscripcion
    template_name = "cuotas/inscripcion_confirm_delete.html"
    success_url = reverse_lazy("cuotas:inscripcion_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Inscripción eliminada correctamente.")
        return super().delete(request, *args, **kwargs)


class InscripcionDetailView(LoginRequiredMixin, DetailView):
    model = Inscripcion
    template_name = "cuotas/inscripcion_detail.html"
    context_object_name = "inscripcion"


# ==========================
# Cuotas
# ==========================
class CuotaListView(LoginRequiredMixin, ListView):
    model = Cuota
    template_name = "cuotas/cuota_list.html"
    context_object_name = "cuotas"
    paginate_by = 30

    def get_queryset(self):
        qs = super().get_queryset().select_related("inscripcion", "inscripcion__estudiante", "inscripcion__ciclo", "inscripcion__nivel", "inscripcion__curso")
        inscripcion_id = self.kwargs.get("inscripcion_id")
        if inscripcion_id:
            qs = qs.filter(inscripcion_id=inscripcion_id)
        pagada = self.request.GET.get("pagada")
        if pagada == "si":
            qs = qs.filter(pagada=True)
        elif pagada == "no":
            qs = qs.filter(pagada=False)
        mes = self.request.GET.get("mes")
        if mes:
            qs = qs.filter(mes=mes)
        return qs


class CuotaUpdateView(LoginRequiredMixin, UpdateView):
    model = Cuota
    form_class = CuotaForm
    template_name = "cuotas/cuota_form.html"

    def get_success_url(self):
        messages.success(self.request, "Cuota actualizada correctamente.")
        return reverse_lazy("cuotas:cuota_list_by_inscripcion", kwargs={"inscripcion_id": self.object.inscripcion_id})


class CuotaDeleteView(LoginRequiredMixin, DeleteView):
    model = Cuota
    template_name = "cuotas/cuota_confirm_delete.html"

    def get_success_url(self):
        messages.success(self.request, "Cuota eliminada correctamente.")
        return reverse_lazy("cuotas:cuota_list_by_inscripcion", kwargs={"inscripcion_id": self.object.inscripcion_id})