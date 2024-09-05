from django.urls import path
from apps.administracion.views import home

urlpatterns = [
    path('', home, name='home'),
]