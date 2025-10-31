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
    path('filtrar-montos/', views.filtrar_montos, name='filtrar_montos'),

    # 🎓 Becas y Beneficios
    path('administracion/becas/', views.lista_becas, name='lista_becas'),
    path('administracion/becas/crear/', views.crear_beca, name='crear_beca'),
    path('administracion/becas/<int:pk>/editar/', views.editar_beca, name='editar_beca'),
    path('administracion/becas/<int:pk>/eliminar/', views.eliminar_beca, name='eliminar_beca'),
    path('becas/estudiantes/', views.estudiantes_becas_activas, name='estudiantes_becas_activas'),
    path('becas/asignar/', views.asignar_beca_general, name='asignar_beca_general'),
    path('filtrar-becas/', views.filtrar_becas, name='filtrar_becas'),
    path('filtrar-estudiantes-becas/', views.filtrar_estudiantes_becas, name='filtrar_estudiantes_becas'),

    # 🎓 Inscripción
    path('inscribir/<int:estudiante_id>/', views.inscribir_estudiante, name='inscribir_estudiante'),
    path('eliminar-inscripcion/<int:inscripcion_id>/', views.eliminar_inscripcion, name='eliminar_inscripcion'),
    path('pago/registrar/<int:cuota_id>/', views.registrar_pago, name='registrar_pago'),
    path('pago/deshacer/<int:cuota_id>/', views.deshacer_pago, name='deshacer_pago'),

    path('generar-pdf-deuda/<int:estudiante_id>/', views.generar_pdf_deuda, name='generar_pdf_deuda'),
    path('ver-cuotas/<int:estudiante_id>/', views.ver_cuotas_estudiante, name='ver_cuotas_estudiante'),

]