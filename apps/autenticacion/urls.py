# apps/autenticacion/urls.py
from django.urls import path
from .views import login_view, register_view, logout_view

urlpatterns = [
    path('iniciar-sesion/', login_view, name='iniciar_sesion'),
    path('registrar/', register_view, name='registrar'),
    path('cerrar-sesion/', logout_view, name='cerrar_sesion'),
]
