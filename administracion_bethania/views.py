"""from django.shortcuts import render

from django.contrib.auth.decorators import login_required

def error_404(request, exception):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)

def trigger_error(request):
    # Esta vista genera un error del servidor intencionalmente
    division_por_cero = 1 / 0

@login_required
def forbidden_view(request):
    # Obtener la acción que el usuario intentó realizar desde la URL
    next_url = request.GET.get('next', '/')

    # Pasamos el nombre del usuario y la acción intentada al template
    context = {
        'usuario': request.user,
        'accion_intentada': next_url
    }
    
    return render(request, 'forbidden.html', context)
"""


from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# ======================================================
#   VISTAS DE MANEJO DE ERRORES GLOBALES (HTTP HANDLERS)
# ======================================================

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from django.core.exceptions import PermissionDenied
from django.shortcuts import render


# ======================================================
#   VISTAS DE PRUEBA DE ERRORES (USAN TUS PLANTILLAS)
# ======================================================

def test_errors_menu(request):
    """
    Muestra un menú con enlaces para probar los errores personalizados.
    """
    return render(request, 'errors/test_menu.html')


def force_400(request):
    """
    Fuerza un error 400 (Bad Request) y renderiza tu plantilla personalizada.
    """
    return render(request, 'errors/400.html', status=400)


def force_403(request):
    """
    Fuerza un error 403 (Forbidden) y renderiza tu plantilla personalizada.
    """
    # En lugar de lanzar la excepción, renderizamos tu template directamente:
    return render(request, 'errors/403.html', status=403)


def force_404(request):
    """
    Fuerza un error 404 (Not Found) y renderiza tu plantilla personalizada.
    """
    return render(request, 'errors/404.html', status=404)


def force_500(request):
    """
    Fuerza un error 500 (Internal Server Error) y renderiza tu plantilla personalizada.
    """
    return render(request, 'errors/500.html', status=500)





def error_404_view(request, exception):
    """
    Error 404 - Página no encontrada.
    Se muestra cuando el usuario intenta acceder a una URL inexistente.
    """
    return render(request, 'errors/404.html', status=404)


def error_500_view(request):
    """
    Error 500 - Error interno del servidor.
    Se muestra cuando ocurre una excepción no controlada.
    """
    return render(request, 'errors/500.html', status=500)


def error_400_view(request, exception):
    """
    Error 400 - Solicitud incorrecta (Bad Request).
    """
    return render(request, 'errors/400.html', status=400)


@login_required
def forbidden_view(request, exception=None):
    """
    Error 403 - Acceso prohibido.
    Se muestra cuando el usuario intenta acceder a algo sin permisos.
    """
    next_url = request.GET.get('next', '/')
    context = {
        'usuario': request.user,
        'accion_intentada': next_url,
    }
    return render(request, 'errors/403.html', context, status=403)


def trigger_error(request):
    """
    Vista de prueba para forzar un error 500 (solo para desarrollo).
    """
    division_por_cero = 1 / 0  # Provoca ZeroDivisionError intencionalmente
