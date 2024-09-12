from django.urls import path
from . import views


app_name = 'cuotas' 

urlpatterns = [
    path('habilitar_ciclo_lectivo/', views.habilitar_ciclo_lectivo, name='habilitar_ciclo_lectivo'),
    path('consultar_ciclo_lectivo/', views.consultar_ciclo_lectivo, name='consultar_ciclo_lectivo'),
    path('inscribir_alumno/', views.inscribir_alumno, name='inscribir_alumno'),
    path('pago_cuotas/', views.pago_cuotas, name='pago_cuotas'),
    path('consultar_deudas/', views.consultar_deudas, name='consultar_deudas'),
    path('detalle_deuda/<int:alumno_id>/', views.detalle_deuda, name='detalle_deuda'),
]



"""from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cuotas_list/', views.cuotas_list, name='cuotas_list'),
    path('consulta_comprobantes/', views.consulta_comprobantes, name='consulta_comprobantes'),
    path('inscripcion/', views.inscripcion, name='inscripcion'),
    path('habilitar_año_lectivo/', views.habilitar_año_lectivo, name='habilitar_año_lectivo'),
    path('crear_meses/', views.crear_meses, name='crear_meses'),
    path('cobro_cuotas/', views.cobro_cuotas, name='cobro_cuotas'),
    path('pagar_inscripcion/', views.pagar_inscripcion, name='pagar_inscripcion'),
    path('actualizar_monto_global_inscripcion/', views.actualizar_monto_global_inscripcion, name='actualizar_monto_global_inscripcion'),
    path('consultar_cuotas/', views.consultar_cuotas, name='consultar_cuotas'),
    path('registrar_pago/', views.registrar_pago, name='registrar_pago'),
    path('estado_cuotas/', views.estado_cuotas, name='estado_cuotas'),
]"""


