from django.views.generic import ListView
from django.shortcuts import render
from django.db.models import Count, Q
from apps.administracion_alumnos.models import (
    Estudiante,
    Inscripcion,
    ContactoEstudiante,
    EstadoDocumentacion,
)

# ============================
# PANEL PRINCIPAL
# ============================
def panel(request):
    # --- KPIs básicos ---
    total_estudiantes = Estudiante.objects.count()
    total_con_inscripcion = Inscripcion.objects.count()

    # Estado de documentación (case-insensitive)
    aprobados = EstadoDocumentacion.objects.filter(estado__iexact='Aprobado').count()
    pendientes = EstadoDocumentacion.objects.filter(estado__iexact='Pendiente').count()
    total_con_estado = aprobados + pendientes
    porc_aprobado = round((aprobados / total_con_estado) * 100, 2) if total_con_estado else 0.0
    porc_pendiente = round((pendientes / total_con_estado) * 100, 2) if total_con_estado else 0.0

    # Distribución por nivel
    niveles_qs = (
        Inscripcion.objects.values("nivel_estudiante")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    niveles_labels = [i["nivel_estudiante"] or "Sin nivel" for i in niveles_qs]
    niveles_data = [i["total"] for i in niveles_qs]

    # Distribución por turno
    turnos_qs = (
        Inscripcion.objects.values("turno_estudiante")
        .annotate(total=Count("id"))
        .order_by("turno_estudiante")
    )
    turnos_labels = [t["turno_estudiante"] or "Sin turno" for t in turnos_qs]
    turnos_data = [t["total"] for t in turnos_qs]

    # Top 5 ciudades (ContactoEstudiante)
    ciudades_qs = (
        ContactoEstudiante.objects.values("ciudad_estudiante")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )
    ciudades_labels = [c["ciudad_estudiante"] or "Sin ciudad" for c in ciudades_qs]
    ciudades_data = [c["total"] for c in ciudades_qs]

    # Fotos pendientes
    fotos_pendientes = Inscripcion.objects.filter(
        Q(foto_estudiante__isnull=True) | Q(foto_estudiante__exact="")
    ).count()

    # Contacto incompleto
    contacto_incompleto = ContactoEstudiante.objects.filter(
        Q(email_estudiante__isnull=True) | Q(email_estudiante__exact="") |
        Q(tel_cel_estudiante__isnull=True) | Q(tel_cel_estudiante__exact="")
    ).count()

    # Últimos 10 estudiantes (si NO hay OneToOne a "inscripcion", quitar select_related)
    ultimos_estudiantes = (
        Estudiante.objects
        # .select_related("inscripcion")  # ← quitalo si no es OneToOne
        .order_by("-id")[:10]
    )

    context = {
        "total_estudiantes": total_estudiantes,
        "total_con_inscripcion": total_con_inscripcion,
        "aprobados": aprobados,
        "pendientes": pendientes,
        "porc_aprobado": f"{porc_aprobado:.2f}",
        "porc_pendiente": f"{porc_pendiente:.2f}",
        "fotos_pendientes": fotos_pendientes,
        "contacto_incompleto": contacto_incompleto,
        "niveles_labels": niveles_labels,
        "niveles_data": niveles_data,
        "turnos_labels": turnos_labels,
        "turnos_data": turnos_data,
        "ciudades_labels": ciudades_labels,
        "ciudades_data": ciudades_data,
        "ultimos_estudiantes": ultimos_estudiantes,
    }
    return render(request, "dashboard/panel.html", context)


# ============================
# HELPERS DE FILTRO (drill-down)
# ============================
def _qs_estudiantes_filtrado(request):
    qs = Estudiante.objects.all()
    f = request.GET.get("f")
    nivel = request.GET.get("nivel")
    turno = request.GET.get("turno")
    ciudad = request.GET.get("ciudad")
    busq = request.GET.get("q")

    # Por estado de documentación
    if f == "doc:aprobado":
        qs = qs.filter(
            id__in=EstadoDocumentacion.objects.filter(estado__iexact="Aprobado")
            .values("estudiante_id")
        )
    elif f == "doc:pendiente":
        qs = qs.filter(
            id__in=EstadoDocumentacion.objects.filter(estado__iexact="Pendiente")
            .values("estudiante_id")
        )

    # Contacto incompleto
    if f == "contacto:incompleto":
        qs = qs.filter(
            id__in=ContactoEstudiante.objects.filter(
                Q(email_estudiante__isnull=True) | Q(email_estudiante="") |
                Q(tel_cel_estudiante__isnull=True) | Q(tel_cel_estudiante="")
            ).values("estudiante_id")
        )

    # Filtros por Inscripción
    if nivel:
        qs = qs.filter(
            id__in=Inscripcion.objects.filter(nivel_estudiante=nivel).values("estudiante_id")
        )
    if turno:
        qs = qs.filter(
            id__in=Inscripcion.objects.filter(turno_estudiante=turno).values("estudiante_id")
        )

    # Filtro por ciudad (Contacto)
    if ciudad:
        qs = qs.filter(
            id__in=ContactoEstudiante.objects.filter(ciudad_estudiante=ciudad).values("estudiante_id")
        )

    # Búsqueda rápida (en Estudiante: ¡sin 'estudiante__'!)
    if busq:
        qs = qs.filter(
            Q(apellidos_estudiante__icontains=busq) |
            Q(nombres_estudiante__icontains=busq) |
            Q(cuil_estudiante__icontains=busq)
        )
    return qs.distinct()


def _qs_inscripciones_filtrado(request):
    qs = Inscripcion.objects.select_related("estudiante")
    nivel = request.GET.get("nivel")
    turno = request.GET.get("turno")
    fotos = request.GET.get("fotos")
    busq = request.GET.get("q")

    if nivel:
        qs = qs.filter(nivel_estudiante=nivel)
    if turno:
        qs = qs.filter(turno_estudiante=turno)
    if fotos == "pendientes":
        qs = qs.filter(Q(foto_estudiante__isnull=True) | Q(foto_estudiante=""))

    # Búsqueda por campos REALES del estudiante
    if busq:
        qs = qs.filter(
            Q(estudiante__apellidos_estudiante__icontains=busq) |
            Q(estudiante__nombres_estudiante__icontains=busq) |
            Q(estudiante__cuil_estudiante__icontains=busq)
        )
    return qs


def _qs_contactos_filtrado(request):
    qs = ContactoEstudiante.objects.select_related("estudiante")
    incompletos = request.GET.get("incompletos")
    ciudad = request.GET.get("ciudad")
    busq = request.GET.get("q")

    if incompletos == "1":
        qs = qs.filter(
            Q(email_estudiante__isnull=True) | Q(email_estudiante="") |
            Q(tel_cel_estudiante__isnull=True) | Q(tel_cel_estudiante="")
        )
    if ciudad:
        qs = qs.filter(ciudad_estudiante=ciudad)

    # Búsqueda por campos REALES del estudiante
    if busq:
        qs = qs.filter(
            Q(estudiante__apellidos_estudiante__icontains=busq) |
            Q(estudiante__nombres_estudiante__icontains=busq) |
            Q(estudiante__cuil_estudiante__icontains=busq)
        )
    return qs


# ============================
# LISTADOS GENÉRICOS
# ============================
class ListaBase(ListView):
    paginate_by = 25
    template_name = "dashboard/lista_generica.html"
    context_object_name = "rows"
    page_kwarg = "page"

    titulo = ""
    columnas = []  # [(header, accessor)]
    tipo = ""      # para condicionales en template

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = self.titulo
        ctx["columnas"] = self.columnas
        ctx["tipo"] = self.tipo
        ctx["querystring"] = self.request.GET.urlencode()
        return ctx


class ListaEstudiantesView(ListaBase):
    titulo = "Estudiantes"
    tipo = "estudiantes"
    columnas = [
        ("ID", "id"),
        ("Apellidos", "apellidos_estudiante"),
        ("Nombres", "nombres_estudiante"),
        ("CUIL", "cuil_estudiante"),
    ]
    def get_queryset(self):
        return _qs_estudiantes_filtrado(self.request).order_by("-id")


class ListaInscripcionesView(ListaBase):
    titulo = "Inscripciones"
    tipo = "inscripciones"
    columnas = [
        ("ID", "id"),
        ("Estudiante", "estudiante"),
        ("Nivel", "nivel_estudiante"),
        ("Turno", "turno_estudiante"),
    ]
    def get_queryset(self):
        return _qs_inscripciones_filtrado(self.request).order_by("-id")


class ListaContactosView(ListaBase):
    titulo = "Contactos"
    tipo = "contactos"
    columnas = [
        ("ID", "id"),
        ("Estudiante", "estudiante"),
        ("Email", "email_estudiante"),
        ("Celular", "tel_cel_estudiante"),
        ("Ciudad", "ciudad_estudiante"),
    ]
    def get_queryset(self):
        return _qs_contactos_filtrado(self.request).order_by("-id")
