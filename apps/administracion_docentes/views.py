from django.shortcuts import render

def index(request):
    return render(request, 'administracion_docentes/index.html')
