from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'cuotas' 

urlpatterns = [
    path('habilitar_ciclo_lectivo/', views.habilitar_ciclo_lectivo, name='habilitar_ciclo_lectivo'),
    path('actualizar_montos/', views.actualizar_montos, name='actualizar_montos'),
    path('listar_montos/', views.listar_montos, name='listar_montos'),
    path('generar_pdf_montos/', views.generar_pdf_montos_view, name='generar_pdf_montos'),
    path('pdf_montos_reportlab/', views.generar_pdf_montos_reportlab, name='pdf_montos_reportlab'),
    path('consultar_ciclo_lectivo/', views.consultar_ciclo_lectivo, name='consultar_ciclo_lectivo'),
    path('listar_ciclos_lectivos/', views.listar_ciclos_lectivos, name='listar_ciclos_lectivos'),
    path('eliminar_ciclo_lectivo/<str:año_lectivo>/', views.eliminar_ciclo_lectivo, name='eliminar_ciclo_lectivo'),

    path('pago_cuotas/', views.pago_cuotas, name='pago_cuotas'),
    path('consultar_deudas/', views.consultar_deudas, name='consultar_deudas'),
    path('detalle_deuda/<int:alumno_id>/', views.detalle_deuda, name='detalle_deuda'),
    path('listar-alumnos/', views.listar_alumnos_por_ciclo_lectivo, name='listar_alumnos_por_ciclo_lectivo'),
    path('lista-fotos-estudiantes/', views.lista_fotos_estudiantes, name='lista_fotos_estudiantes'),
    path('crear/', views.crear_comprobante_pago,name='crear_comprobante_pago'),
    path('listar/', views.listar_comprobantes, name='listar_comprobantes'),
    path('editar/<int:pk>/', views.editar_comprobante_pago, name='editar_comprobante_pago'),
    path('eliminar/<int:pk>/', views.eliminar_comprobante_pago, name='eliminar_comprobante_pago'),
    path('inscribir_alumno/', views.buscar_estudiantes_aprobados, name='inscribir_alumno'),
    path('buscar_cuotas_estudiante/', views.buscar_cuotas_estudiante, name='buscar_cuotas_estudiante'),

    path('buscar_comprobantes/', views.buscar_comprobantes, name='buscar_comprobantes'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
