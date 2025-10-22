from django.urls import path
from django.contrib.auth import views as auth_views
from .views import login_view, register_view, logout_view, editar_perfil, ver_perfil

urlpatterns = [
    # 🔐 Autenticación
    path('iniciar-sesion/', login_view, name='iniciar_sesion'),
    path('registrar/', register_view, name='registrar'),
    path('cerrar-sesion/', logout_view, name='cerrar_sesion'),

    # 👤 Perfil
    path('perfil/', ver_perfil, name='ver_perfil'),
    path('editar-perfil/', editar_perfil, name='editar_perfil'),

    # 🔑 Cambio de contraseña
    path('cambiar-contraseña/', auth_views.PasswordChangeView.as_view(
        template_name='autenticacion/cambiar_contraseña.html',
        success_url='/autenticacion/perfil/'
    ), name='cambiar_contraseña'),
]
