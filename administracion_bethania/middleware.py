# administracion_bethania/middleware.py

from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

EXEMPT_PREFIXES = (
    "/admin/",                         # Todo el admin (incluye /admin/login/)
    "/autenticacion/iniciar-sesion/",  # Tu login público
    "/static/",
    "/media/",
)

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Resolvemos el path del LOGIN_URL para evitar bucles
        try:
            self.login_path = reverse(settings.LOGIN_URL)
        except Exception:
            # Si por algún motivo no se puede resolver, usamos el string tal cual
            self.login_path = f"/{settings.LOGIN_URL.strip('/')}/"

    def __call__(self, request):
        path = request.path

        # 1) No interceptar rutas exentas
        if path.startswith(EXEMPT_PREFIXES):
            return self.get_response(request)

        # 2) No interceptar el propio login (evita bucle)
        if path == self.login_path:
            return self.get_response(request)

        # 3) Si no está autenticado → redirigir al login con "next"
        if not getattr(request, "user", None) or not request.user.is_authenticated:
            qs = urlencode({"next": request.get_full_path()})
            return redirect(f"{self.login_path}?{qs}")

        # 4) Caso normal
        return self.get_response(request)
