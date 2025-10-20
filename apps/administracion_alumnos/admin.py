from django.contrib import admin
from .models import Estudiante, EstadoDocumentacion

admin.site.register(EstadoDocumentacion)

@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    search_fields = (
        "^apellidos_estudiante",   # empieza con…
        "^nombres_estudiante",
        "=dni_estudiante",         # coincidencia exacta
        "=cuil_estudiante",
    )


    # 🧾 Campos visibles en la lista del admin
    list_display = (
        "apellidos_estudiante",
        "nombres_estudiante",
        "dni_estudiante",
        "sexo_estudiante",
    )

    # 🧩 Filtros laterales opcionales
    list_filter = ("sexo_estudiante",)

    # 🗂 Orden por defecto
    ordering = ("apellidos_estudiante",)
