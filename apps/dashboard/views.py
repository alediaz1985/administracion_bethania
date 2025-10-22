# apps/dashboard/views.py
from django.shortcuts import render
from django.db.models import Count, Q
from apps.administracion_alumnos.models import (
    Estudiante,
    Inscripcion,
    ContactoEstudiante,
    EstadoDocumentacion,
)


def panel(request):
    # --- KPIs básicos ---
    total_estudiantes = Estudiante.objects.count()
    total_con_inscripcion = Inscripcion.objects.count()

    # Estado de documentación (case-insensitive para evitar inconsistencias)
    aprobados = EstadoDocumentacion.objects.filter(estado__iexact='Aprobado').count()
    pendientes = EstadoDocumentacion.objects.filter(estado__iexact='Pendiente').count()
    total_con_estado = aprobados + pendientes
    porc_aprobado = round((aprobados / total_con_estado) * 100, 2) if total_con_estado else 0.0
    porc_pendiente = round((pendientes / total_con_estado) * 100, 2) if total_con_estado else 0.0

    # Distribución por nivel (según Inscripcion.nivel_estudiante)
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

    # Top 5 ciudades (desde ContactoEstudiante)
    ciudades_qs = (
        ContactoEstudiante.objects.values("ciudad_estudiante")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )
    ciudades_labels = [c["ciudad_estudiante"] or "Sin ciudad" for c in ciudades_qs]
    ciudades_data = [c["total"] for c in ciudades_qs]

    # Fotos pendientes (enlace vacío o nulo en Inscripcion.foto_estudiante)
    fotos_pendientes = Inscripcion.objects.filter(
        Q(foto_estudiante__isnull=True) | Q(foto_estudiante__exact="")
    ).count()

    # Contacto incompleto (sin email o sin celular)
    contacto_incompleto = ContactoEstudiante.objects.filter(
        Q(email_estudiante__isnull=True) | Q(email_estudiante__exact="") |
        Q(tel_cel_estudiante__isnull=True) | Q(tel_cel_estudiante__exact="")
    ).count()

    # Últimos 10 estudiantes (fallback por id desc si no hay timestamps)
    ultimos_estudiantes = (
        Estudiante.objects
        .select_related("inscripcion")
        .order_by("-id")[:10]
    )

    context = {
        # KPIs
        "total_estudiantes": total_estudiantes,
        "total_con_inscripcion": total_con_inscripcion,
        "aprobados": aprobados,
        "pendientes": pendientes,
        "porc_aprobado": f"{porc_aprobado:.2f}",
        "porc_pendiente": f"{porc_pendiente:.2f}",
        "fotos_pendientes": fotos_pendientes,
        "contacto_incompleto": contacto_incompleto,

        # Gráficos
        "niveles_labels": niveles_labels,
        "niveles_data": niveles_data,
        "turnos_labels": turnos_labels,
        "turnos_data": turnos_data,
        "ciudades_labels": ciudades_labels,
        "ciudades_data": ciudades_data,

        # Tabla
        "ultimos_estudiantes": ultimos_estudiantes,
    }
    return render(request, "dashboard/panel.html", context)
