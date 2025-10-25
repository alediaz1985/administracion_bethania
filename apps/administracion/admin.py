from django.contrib import admin
from .models import (
    CicloLectivo, Nivel, Subnivel, MontoNivel,
    Beca, InscripcionAdministrativa, Cuota, Pago
)

@admin.register(CicloLectivo)
class CicloLectivoAdmin(admin.ModelAdmin):
    list_display = ('anio', 'fecha_inicio', 'fecha_fin', 'activo')
    list_filter = ('activo',)
    search_fields = ('anio',)


@admin.register(MontoNivel)
class MontoNivelAdmin(admin.ModelAdmin):
    list_display = ('ciclo', 'nivel', 'monto_cuota', 'monto_inscripcion', 'fecha_vigencia_desde', 'activo')
    list_filter = ('nivel', 'ciclo', 'activo')
    search_fields = ('nivel__nombre',)


@admin.register(Beca)
class BecaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'valor', 'activa')
    list_filter = ('activa',)
    search_fields = ('nombre',)


@admin.register(Nivel)
class NivelAdmin(admin.ModelAdmin):
    list_display = ('nombre',)


@admin.register(Subnivel)
class SubnivelAdmin(admin.ModelAdmin):
    list_display = ('nivel', 'nombre')
    list_filter = ('nivel',)
    search_fields = ('nombre',)


@admin.register(InscripcionAdministrativa)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'ciclo', 'nivel', 'subnivel', 'turno', 'activo')
    list_filter = ('ciclo', 'nivel', 'turno', 'activo')
    search_fields = ('estudiante__apellidos_estudiante', 'estudiante__nombres_estudiante')


@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    list_display = ('inscripcion', 'mes', 'anio', 'monto_final', 'estado')
    list_filter = ('anio', 'estado')
    search_fields = ('inscripcion__estudiante__apellidos_estudiante',)


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_pago', 'metodo_pago', 'monto_total')
    list_filter = ('metodo_pago',)
    search_fields = ('observaciones',)
