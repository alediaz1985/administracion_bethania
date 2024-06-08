from django.shortcuts import render

def niveles_list(request):
    return render(request, 'niveles/niveles_list.html')

def registrar_nivel(request):
    return render(request, 'niveles/registrar_nivel.html')

def editar_nivel(request):
    return render(request, 'niveles/editar_nivel.html')
