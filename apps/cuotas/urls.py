from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.urls import path
from .views import (
    CursoListView, CursoCreateView, CursoUpdateView, CursoDeleteView,
    cursos_por_nivel_api
)

from django.urls import path
from .views import (
    TarifaNivelListView,
    TarifaNivelCreateView,
    TarifaNivelUpdateView,
    TarifaNivelDeleteView,
)



app_name = "cuotas"

urlpatterns = [
    # ========================
    # 🔹 HOME DE CUOTAS
    # ========================
    path("", views.cuotas_home, name="home"),

    # ========================
    # 📅 CICLOS LECTIVOS
    # ========================

    path("ciclos/", views.ciclos_list, name="ciclo_list"),             # GET muestra pestañas
    path("ciclos/crear/", views.ciclo_create, name="ciclo_create"),    # POST del form
    path("ciclos/<int:pk>/activar/", views.activar_ciclo, name="activar_ciclo"),


    # ========================
    # 🏫 NIVELES
    # ========================
    path("niveles/", views.NivelListView.as_view(), name="nivel_list"),
    path("niveles/nuevo/", views.NivelCreateView.as_view(), name="nivel_create"),
    path("niveles/<int:pk>/editar/", views.NivelUpdateView.as_view(), name="nivel_update"),

    # ========================
    # 🎓 CURSOS
    # ========================

    path("cursos/", CursoListView.as_view(), name="curso_list"),
    path("cursos/nuevo/", CursoCreateView.as_view(), name="curso_create"),
    path("cursos/<int:pk>/editar/", CursoUpdateView.as_view(), name="curso_update"),
    path("cursos/<int:pk>/eliminar/", CursoDeleteView.as_view(), name="curso_delete"),

    # opcional API
    path("api/cursos", cursos_por_nivel_api, name="api_cursos_por_nivel"),

    # ========================
    # 💰 PLANES / TARIFAS
    # ========================

    path("tarifas/", views.TarifaNivelListView.as_view(), name="tarifa_nivel_list"),
    path("tarifas/nueva/", views.TarifaNivelCreateView.as_view(), name="tarifa_nivel_create"),
    path("tarifas/<int:pk>/editar/", views.TarifaNivelUpdateView.as_view(), name="tarifa_nivel_update"),
    path("tarifas/<int:pk>/eliminar/", views.TarifaNivelDeleteView.as_view(), name="tarifa_nivel_delete"),


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
    path("inscripcion/<int:inscripcion_id>/cuotas/", views.cuota_list, name="cuota_list"),
    path("cuota/<int:cuota_id>/cobrar/", views.cuota_cobrar, name="cuota_cobrar"),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
