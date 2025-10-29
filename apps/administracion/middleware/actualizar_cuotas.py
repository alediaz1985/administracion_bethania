# apps/administracion/middleware/actualizar_cuotas.py

from datetime import date
from apps.administracion.utils import actualizar_cuotas_vencidas

class ActualizarCuotasMiddleware:
    """
    Middleware que actualiza las cuotas vencidas una vez por día
    cuando un usuario autenticado realiza una solicitud.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Solo ejecutar si el usuario está logueado y no es una ruta estática
        if request.user.is_authenticated and not request.path.startswith('/static/'):
            hoy = str(date.today())
            ultima_actualizacion = request.session.get('ultima_actualizacion_cuotas')

            # Si no se actualizó hoy, ejecutar la función y registrar la fecha
            if ultima_actualizacion != hoy:
                print("🔄 [Middleware] Ejecutando actualización de cuotas vencidas...")
                actualizar_cuotas_vencidas()
                request.session['ultima_actualizacion_cuotas'] = hoy
                print("✅ [Middleware] Cuotas vencidas actualizadas correctamente.")
            else:
                # Solo para control: comentar si no querés ver esto cada vez
                print("⏩ [Middleware] Cuotas ya actualizadas hoy, se omite ejecución.")

        # Continuar con la petición normal
        response = self.get_response(request)
        return response
