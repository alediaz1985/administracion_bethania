from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import DocenteForm
from .models import Docente

def listar_docentes(request):
    docentes = Docente.objects.all()
    return render(request, 'administracion_docentes/listar_docentes.html', {'docentes': docentes})

def consultar_docente(request):
    if request.method == 'POST':
        cuil = request.POST.get('cuil')
        try:
            docente = Docente.objects.get(cuil=cuil)
        except Docente.DoesNotExist:
            docente = None
        return render(request, 'administracion_docentes/consultar_docente.html', {'docente': docente})
    return render(request, 'administracion_docentes/consultar_docente.html')

def ver_datos_docente(request, cuil):
    docente = get_object_or_404(Docente, cuil=cuil)
    return render(request, 'administracion_docentes/ver_datos_docente.html', {'docente': docente})

def registrar_docente(request):
    if request.method == 'POST':
        form = DocenteForm(request.POST)
        if form.is_valid():
            cuil_supervisor = form.cleaned_data.get('cuil_supervisor')
            if cuil_supervisor and not Docente.objects.filter(cuil=cuil_supervisor).exists():
                messages.error(request, 'El CUIL del supervisor no existe. Por favor, verifique los datos ingresados.')
            else:
                form.save()
                messages.success(request, 'Docente registrado exitosamente.')
                return redirect('listar_docentes')
        else:
            messages.error(request, 'Hubo un error al registrar el docente. Por favor, verifica los datos ingresados.')
    else:
        form = DocenteForm()
    return render(request, 'administracion_docentes/registrar_docente.html', {'form': form})

def editar_docente(request, cuil):
    docente = get_object_or_404(Docente, cuil=cuil)
    if request.method == 'POST':
        form = DocenteForm(request.POST, instance=docente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Docente actualizado exitosamente.')
            return redirect('listar_docentes')
    else:
        form = DocenteForm(instance=docente)
    return render(request, 'administracion_docentes/editar_docente.html', {'form': form, 'docente': docente})

def eliminar_docente(request, cuil):
    docente = get_object_or_404(Docente, cuil=cuil)
    if request.method == 'POST':
        docente.delete()
        messages.success(request, 'Docente eliminado exitosamente.')
        return redirect('listar_docentes')
    return render(request, 'administracion_docentes/eliminar_docente.html', {'docente': docente})
