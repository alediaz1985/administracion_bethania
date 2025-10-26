# apps/dashboard/urls.py
from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # Panel principal
    path("", views.panel, name="panel"),

    # Listados/drill-downs
    path("lista/estudiantes/", views.ListaEstudiantesView.as_view(), name="lista_estudiantes"),
    path("lista/inscripciones/", views.ListaInscripcionesView.as_view(), name="lista_inscripciones"),
    path("lista/contactos/", views.ListaContactosView.as_view(), name="lista_contactos"),
]
