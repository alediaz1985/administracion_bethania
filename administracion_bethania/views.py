from django.shortcuts import render

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
