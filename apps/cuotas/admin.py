from django.contrib import admin
from .models import DatosGlobales, Inscripcion, Cuota, Mes

# Registra los modelos para que aparezcan en el admin
admin.site.register(DatosGlobales)
admin.site.register(Inscripcion)
admin.site.register(Cuota)
admin.site.register(Mes)