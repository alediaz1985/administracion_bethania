from django.contrib import admin
from .models import (
    Estudiante,
    Inscripcion,
    InformacionAcademica,
    ContactoEstudiante,
    SaludEstudiante,
    Responsable,
    Documentacion,
    EstadoDocumentacion,
)


# ============================================================
# 🧍 ESTUDIANTE
# ============================================================
@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    search_fields = (
        "^apellidos_estudiante",  # comienza con
        "^nombres_estudiante",
        "=dni_estudiante",        # coincidencia exacta
        "=cuil_estudiante",
    )
    list_display = (
        "apellidos_estudiante",
        "nombres_estudiante",
        "dni_estudiante",
        "sexo_estudiante",
    )
    list_filter = ("sexo_estudiante",)
    ordering = ("apellidos_estudiante",)


# ============================================================
# 🏫 INSCRIPCIÓN
# ============================================================
@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = (
        "estudiante",
        "nivel_estudiante",
        "curso_anio_estudiante",
        "turno_estudiante",
        "nivel_ensenanza",
    )
    search_fields = ("estudiante__apellidos_estudiante", "estudiante__nombres_estudiante")
    list_filter = ("nivel_estudiante", "turno_estudiante")


# ============================================================
# 🎓 INFORMACIÓN ACADÉMICA
# ============================================================
@admin.register(InformacionAcademica)
class InformacionAcademicaAdmin(admin.ModelAdmin):
    list_display = (
        "estudiante",
        "anio_cursado",
        "donde_cursado",
        "asignaturas_pendientes",
    )
    search_fields = ("estudiante__apellidos_estudiante", "estudiante__nombres_estudiante")


# ============================================================
# 🏠 CONTACTO / DOMICILIO
# ============================================================
@admin.register(ContactoEstudiante)
class ContactoEstudianteAdmin(admin.ModelAdmin):
    list_display = (
        "estudiante",
        "ciudad_estudiante",
        "provincia_estudiante",
        "barrio_estudiante",
        "email_estudiante",
        "tel_cel_estudiante",
    )
    search_fields = ("estudiante__apellidos_estudiante", "email_estudiante", "tel_cel_estudiante")


# ============================================================
# ❤️ SALUD DEL ESTUDIANTE
# ============================================================
@admin.register(SaludEstudiante)
class SaludEstudianteAdmin(admin.ModelAdmin):
    list_display = (
        "estudiante",
        "peso_estudiante",
        "talla_estudiante",
        "obra_social_estudiante",
        "problema_fisico_estudiante",
        "problema_aprendizaje_estudiante",
    )
    search_fields = ("estudiante__apellidos_estudiante", "obra_social_estudiante")


# ============================================================
# 👨‍👩‍👧 RESPONSABLES
# ============================================================
@admin.register(Responsable)
class ResponsableAdmin(admin.ModelAdmin):
    list_display = (
        "estudiante",
        "apellidos",
        "nombres",
        "dni",
        "cuil",
        "ocupacion",
    )
    search_fields = ("apellidos", "nombres", "dni", "cuil")
    list_filter = ("ocupacion",)


# ============================================================
# 📄 DOCUMENTACIÓN
# ============================================================
@admin.register(Documentacion)
class DocumentacionAdmin(admin.ModelAdmin):
    list_display = (
        "estudiante",
        "fecha_contrato",
        "responsable_pago",
        "dni_responsable_pago",
    )
    search_fields = ("estudiante__apellidos_estudiante", "responsable_pago")


# ============================================================
# ✅ ESTADO DE DOCUMENTACIÓN
# ============================================================
@admin.register(EstadoDocumentacion)
class EstadoDocumentacionAdmin(admin.ModelAdmin):
    list_display = ("estudiante", "estado", "fecha_actualizacion")
    list_filter = ("estado",)
    search_fields = ("estudiante__apellidos_estudiante",)
