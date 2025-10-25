from django.urls import path
from . import views

app_name = 'administracion'

urlpatterns = [
    path('', views.home, name='home'),
    path('administracion/', views.home_administracion, name='home_administracion'),

    # 🟩 Secciones del panel administrativo
    path('administracion/ciclos/', views.lista_ciclos, name='lista_ciclos'),
    path('administracion/ciclos/crear/', views.crear_ciclo, name='crear_ciclo'),
    path('administracion/ciclos/<int:pk>/editar/', views.editar_ciclo, name='editar_ciclo'),
    path('administracion/ciclos/<int:pk>/eliminar/', views.eliminar_ciclo, name='eliminar_ciclo'),

    # 💰 Montos por Nivel
    path('administracion/montos/', views.lista_montos, name='lista_montos'),
    path('administracion/montos/crear/', views.crear_monto, name='crear_monto'),
    path('administracion/montos/<int:pk>/editar/', views.editar_monto, name='editar_monto'),
    path('administracion/montos/<int:pk>/eliminar/', views.eliminar_monto, name='eliminar_monto'),

    # 🎓 Becas y Beneficios
    path('administracion/becas/', views.lista_becas, name='lista_becas'),
    path('administracion/becas/crear/', views.crear_beca, name='crear_beca'),
    path('administracion/becas/<int:pk>/editar/', views.editar_beca, name='editar_beca'),
    path('administracion/becas/<int:pk>/eliminar/', views.eliminar_beca, name='eliminar_beca'),

    
    path('inscribir/<int:estudiante_id>/', views.inscribir_estudiante, name='inscribir_estudiante'),
    path('administracion/inscripciones/', views.lista_inscripciones_admin, name='lista_inscripciones_admin'),
    path('administracion/cuotas/', views.lista_cuotas, name='lista_cuotas'),
    path('administracion/pagos/', views.lista_pagos, name='lista_pagos'),
]