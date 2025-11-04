from django.urls import path
from . import views
# apps/comprobantes/urls.py
from django.urls import path


app_name = "comprobantes"  # 👈 importante para los {% url 'comprobantes:...' %} del template

urlpatterns = [
    # --- comprobantes ---
    path("administrar/", views.lista_comprobantes, name="lista_comprobantes"),
    path('cambiar-estado/', views.cambiar_estado_comprobante, name='cambiar_estado_comprobante'),
]
