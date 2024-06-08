from django.urls import path
from . import views

urlpatterns = [
    path('', views.cuotas_list, name='cuotas_list'),
]
