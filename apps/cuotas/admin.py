from django.contrib import admin
from .models import CicloLectivo, Inscripcion, Cuota, Pago, MedioPago

# Admin para Ciclo Lectivo
@admin.register(CicloLectivo)
class CicloLectivoAdmin(admin.ModelAdmin):
    list_display = ('año_lectivo', 'fecha_inicio', 'fecha_fin')
    search_fields = ('año_lectivo',)
    ordering = ('año_lectivo',)


# Admin para Inscripción
@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('cuil_alumno', 'ciclo_lectivo', 'fecha_inscripcion', 'pagada')
    search_fields = ('cuil_alumno__nombres_alumno', 'ciclo_lectivo__año_lectivo')
    ordering = ('fecha_inscripcion',)


# Admin para Cuota
@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    list_display = ('inscripcion', 'mes', 'monto_cuota', 'pagado', 'fecha_pago', 'fuera_de_termino', 'total_a_pagar')
    search_fields = ('inscripcion__cuil_alumno__nombres_alumno',)
    list_filter = ('pagado', 'fuera_de_termino')
    ordering = ('inscripcion', 'mes')


# Admin para Pago
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('cuota', 'fecha_pago', 'monto_pagado', 'medio_pago')
    search_fields = ('cuota__inscripcion__cuil_alumno__nombres_alumno',)
    list_filter = ('medio_pago',)
    ordering = ('fecha_pago',)


# Admin para Medio de Pago
@admin.register(MedioPago)
class MedioPagoAdmin(admin.ModelAdmin):
    list_display = ('nombre_medio_pago',)
    search_fields = ('nombre_medio_pago',)
    ordering = ('nombre_medio_pago',)
