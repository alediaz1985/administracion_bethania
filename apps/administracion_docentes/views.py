from django.shortcuts import render

def docente_list(request):
    return render(request, 'administracion_docentes/docente_list.html')

def consultar_docente(request):
    return render(request, 'administracion_docentes/consultar_docente.html')

def registrar_docente(request):
    return render(request, 'administracion_docentes/registrar_docente.html')
