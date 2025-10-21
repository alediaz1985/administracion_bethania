from django.contrib import admin
from .models import (
    CicloLectivo, Nivel, Curso, TarifaNivel,
    VencimientoMensual, Beneficio, BeneficioInscripcion,
    Inscripcion, Cuota, MedioPago, Pago,
    ComprobanteDrivePago, ComprobantePago
)

# 👇 IMPORTANTE: agregar Estudiante (de la app de alumnos)
from apps.administracion_alumnos.models import Estudiante

# ===============================
# 🔍 Admin para modelos usados en autocomplete
# ===============================

@admin.register(CicloLectivo)
class CicloLectivoAdmin(admin.ModelAdmin):
    list_display = ("anio", "fecha_inicio", "fecha_fin")
    search_fields = ("anio",)
    ordering = ("-anio",)


@admin.register(Nivel)
class NivelAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ("nivel", "nombre", "monto_cuota_override", "monto_inscripcion_override")
    list_filter = ("nivel",)
    search_fields = ("nombre",)




@admin.register(VencimientoMensual)
class VencimientoMensualAdmin(admin.ModelAdmin):
    list_display = ("ciclo", "mes", "dia_ultimo_sin_recargo", "recargo_porcentaje")
    list_filter = ("ciclo",)
    ordering = ("ciclo__anio", "mes")


class BeneficioInscripcionInline(admin.TabularInline):
    model = BeneficioInscripcion
    extra = 0
    autocomplete_fields = ("beneficio",)  # BeneficioAdmin tiene search_fields


@admin.register(Beneficio)
class BeneficioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "porcentaje", "monto_fijo", "prioridad", "activo")
    list_filter = ("tipo", "activo")
    search_fields = ("nombre",)


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ("estudiante", "ciclo", "nivel", "curso", "monto_inscripcion", "fecha_inscripcion")
    list_filter = ("ciclo", "nivel", "curso")
    search_fields = (
        "estudiante__apellidos_estudiante",
        "estudiante__nombres_estudiante",
        "estudiante__dni_estudiante",
        "estudiante__cuil_estudiante",
    )
    autocomplete_fields = ("estudiante", "ciclo", "nivel", "curso")
    list_select_related = ("estudiante", "ciclo", "nivel", "curso")  # 🚀 mejora de rendimiento
    inlines = [BeneficioInscripcionInline]



@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    list_display = ("inscripcion", "mes", "monto_base", "monto_descuentos", "monto_recargos", "total_a_pagar", "pagada")
    list_filter = ("inscripcion__ciclo", "inscripcion__nivel", "mes", "pagada")
    search_fields = ("inscripcion__estudiante__apellidos_estudiante", "inscripcion__estudiante__dni_estudiante")
    autocomplete_fields = ("inscripcion",)  # InscripcionAdmin ya define search_fields


@admin.register(MedioPago)
class MedioPagoAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("cuota", "fecha_pago", "monto_pagado", "medio_pago")
    list_filter = ("medio_pago", "fecha_pago")
    autocomplete_fields = ("cuota", "medio_pago")  # Ambos tienen search_fields


@admin.register(ComprobanteDrivePago)
class ComprobanteDrivePagoAdmin(admin.ModelAdmin):
    list_display = ("id", "correo_electronico", "cuil_estudiante", "cuil_responsable_pago")


# Solo lectura para la tabla externa
@admin.register(ComprobantePago)
class ComprobantePagoAdmin(admin.ModelAdmin):
    list_display = ("email", "marca_temporal", "url_comprobante", "cuil_alumno", "cuil_responsable")
    readonly_fields = ("email", "marca_temporal", "url_comprobante", "cuil_alumno", "cuil_responsable", "ruta_local")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


from django.contrib import admin
from .models import TarifaNivel

@admin.register(TarifaNivel)
class TarifaNivelAdmin(admin.ModelAdmin):
    list_display = ("ciclo", "nivel", "monto_inscripcion", "monto_cuota_mensual")
    list_filter = ("ciclo", "nivel")
    search_fields = ("nivel__nombre", "ciclo__anio")
    ordering = ("ciclo", "nivel")
    autocomplete_fields = ("ciclo", "nivel")
