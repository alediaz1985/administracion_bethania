from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "cuotas"

urlpatterns = [
    # ========================
    # 🔹 HOME DE CUOTAS
    # ========================
    path("", views.cuotas_home, name="home"),

    # ========================
    # 📅 CICLOS LECTIVOS
    # ========================
    path("ciclos/", views.CicloListView.as_view(), name="ciclo_list"),
    path("ciclos/nuevo/", views.CicloCreateView.as_view(), name="ciclo_create"),
    path("ciclos/<int:pk>/editar/", views.CicloUpdateView.as_view(), name="ciclo_update"),
    path("ciclos/<int:ciclo_id>/activar/", views.activar_ciclo, name="ciclo_activar"),
    path("ciclos/", views.CicloListView.as_view(), name="ciclo_list"),

    # ========================
    # 🏫 NIVELES
    # ========================
    path("niveles/", views.NivelListView.as_view(), name="nivel_list"),
    path("niveles/nuevo/", views.NivelCreateView.as_view(), name="nivel_create"),
    path("niveles/<int:pk>/editar/", views.NivelUpdateView.as_view(), name="nivel_update"),

    # ========================
    # 🎓 CURSOS
    # ========================
    path("cursos/", views.CursoListView.as_view(), name="curso_list"),
    path("cursos/nuevo/", views.CursoCreateView.as_view(), name="curso_create"),
    path("cursos/<int:pk>/editar/", views.CursoUpdateView.as_view(), name="curso_update"),

    # ========================
    # 💰 PLANES / TARIFAS
    # ========================
    path("tarifas/", views.TarifaListView.as_view(), name="tarifa_list"),
    path("tarifas/nuevo/", views.TarifaCreateView.as_view(), name="tarifa_create"),
    path("tarifas/<int:pk>/editar/", views.TarifaUpdateView.as_view(), name="tarifa_update"),

    # ========================
    # 🕐 VENCIMIENTOS
    # ========================
    path("vencimientos/", views.VencimientoListView.as_view(), name="vencimiento_list"),
    path("vencimientos/nuevo/", views.VencimientoCreateView.as_view(), name="vencimiento_create"),
    path("vencimientos/<int:pk>/editar/", views.VencimientoUpdateView.as_view(), name="vencimiento_update"),

    # ========================
    # 🎁 BENEFICIOS (DESCUENTOS)
    # ========================
    path("beneficios/", views.BeneficioListView.as_view(), name="beneficio_list"),
    path("beneficios/nuevo/", views.BeneficioCreateView.as_view(), name="beneficio_create"),
    path("beneficios/<int:pk>/editar/", views.BeneficioUpdateView.as_view(), name="beneficio_update"),

    # ========================
    # 🎁 BENEFICIOS INSCRIPCIÓN
    # ========================
    path("beneficios-inscripcion/", views.BeneficioInscripcionListView.as_view(), name="beneficio_insc_list"),
    path("beneficios-inscripcion/nuevo/", views.BeneficioInscripcionCreateView.as_view(), name="beneficio_insc_create"),
    path("beneficios-inscripcion/<int:pk>/editar/", views.BeneficioInscripcionUpdateView.as_view(), name="beneficio_insc_update"),

    # ========================
    # 🧾 INSCRIPCIONES
    # ========================
    path("inscripciones/", views.InscripcionListView.as_view(), name="inscripcion_list"),
    path("inscripciones/nueva/", views.InscripcionCreateView.as_view(), name="inscripcion_create"),
    path("inscripciones/<int:pk>/editar/", views.InscripcionUpdateView.as_view(), name="inscripcion_update"),
    path("inscripciones/<int:pk>/generar-cuotas/", views.generar_cuotas_view, name="inscripcion_generar_cuotas"),
    path("inscripciones/<int:pk>/cuotas/", views.cuotas_por_inscripcion, name="inscripcion_cuotas"),

    # ========================
    # 💳 COBRO DE CUOTAS
    # ========================
    path("cuotas/<int:cuota_id>/cobrar/", views.cobrar_cuota, name="cuota_cobrar"),
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
