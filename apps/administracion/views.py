from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, FileResponse, JsonResponse
from django.template.loader import render_to_string
from apps.administracion.models import CicloLectivo, MontoNivel, Beca
from apps.administracion_alumnos.models import Estudiante
from .forms import CicloLectivoForm, MontoNivelForm, BecaForm

def home(request):
    return render(request, 'home.html')

def home_administracion(request):
    return render(request, 'administracion/home_administracion.html')

# ==============================
# 🗓️ LISTAR CICLOS
# ==============================
def lista_ciclos(request):
    ciclos = CicloLectivo.objects.all().order_by('-anio')
    return render(request, 'administracion/ciclo_lectivo/lista.html', {'ciclos': ciclos})


# ==============================
# ➕ CREAR CICLO (AJAX Modal)
# ==============================
def crear_ciclo(request):
    data = {}
    if request.method == 'POST':
        form = CicloLectivoForm(request.POST)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            ciclos = CicloLectivo.objects.all().order_by('-anio')
            data['html_list'] = render_to_string('administracion/ciclo_lectivo/_tabla.html', {'ciclos': ciclos})
        else:
            data['form_is_valid'] = False
    else:
        form = CicloLectivoForm()

    context = {'form': form}
    data['html_form'] = render_to_string('administracion/ciclo_lectivo/_modal_form.html', context, request=request)
    return JsonResponse(data)


# ==============================
# ✏️ EDITAR CICLO (AJAX Modal)
# ==============================
def editar_ciclo(request, pk):
    ciclo = get_object_or_404(CicloLectivo, pk=pk)
    data = {}
    if request.method == 'POST':
        form = CicloLectivoForm(request.POST, instance=ciclo)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            ciclos = CicloLectivo.objects.all().order_by('-anio')
            data['html_list'] = render_to_string('administracion/ciclo_lectivo/_tabla.html', {'ciclos': ciclos})
        else:
            data['form_is_valid'] = False
    else:
        form = CicloLectivoForm(instance=ciclo)

    context = {'form': form}
    data['html_form'] = render_to_string('administracion/ciclo_lectivo/_modal_form.html', context, request=request)
    return JsonResponse(data)


# ==============================
# 🗑️ ELIMINAR CICLO (AJAX Modal)
# ==============================
def eliminar_ciclo(request, pk):
    ciclo = get_object_or_404(CicloLectivo, pk=pk)
    data = {}
    if request.method == 'POST':
        ciclo.delete()
        data['form_is_valid'] = True
        ciclos = CicloLectivo.objects.all().order_by('-anio')
        data['html_list'] = render_to_string('administracion/ciclo_lectivo/_tabla.html', {'ciclos': ciclos})
    else:
        context = {'ciclo': ciclo}
        data['html_form'] = render_to_string('administracion/ciclo_lectivo/_modal_delete.html', context, request=request)
    return JsonResponse(data)

# ============================================================
# 💰 MONTOS POR NIVEL
# ============================================================
def lista_montos(request):
    montos = MontoNivel.objects.select_related('ciclo', 'nivel').order_by('-ciclo__anio', 'nivel__nombre', '-fecha_vigencia_desde')
    return render(request, 'administracion/monto_nivel/lista.html', {'montos': montos})


def crear_monto(request):
    data = {}
    if request.method == 'POST':
        form = MontoNivelForm(request.POST)
        if form.is_valid():
            nuevo_monto = form.save(commit=False)

            # 🔹 Si hay un monto activo anterior, lo cerramos
            anterior = MontoNivel.objects.filter(
                ciclo=nuevo_monto.ciclo,
                nivel=nuevo_monto.nivel,
                activo=True
            ).exclude(pk=nuevo_monto.pk).first()

            if anterior:
                anterior.activo = False
                anterior.fecha_vigencia_hasta = nuevo_monto.fecha_vigencia_desde
                anterior.save()

            nuevo_monto.save()
            data['form_is_valid'] = True
            montos = MontoNivel.objects.select_related('ciclo', 'nivel').order_by('-ciclo__anio', 'nivel__nombre', '-fecha_vigencia_desde')
            data['html_list'] = render_to_string('administracion/monto_nivel/_tabla.html', {'montos': montos})
        else:
            data['form_is_valid'] = False
    else:
        form = MontoNivelForm()

    context = {'form': form}
    data['html_form'] = render_to_string('administracion/monto_nivel/_modal_form.html', context, request=request)
    return JsonResponse(data)


def editar_monto(request, pk):
    monto = get_object_or_404(MontoNivel, pk=pk)
    data = {}
    if request.method == 'POST':
        form = MontoNivelForm(request.POST, instance=monto)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            montos = MontoNivel.objects.select_related('ciclo', 'nivel').order_by('-ciclo__anio', 'nivel__nombre', '-fecha_vigencia_desde')
            data['html_list'] = render_to_string('administracion/monto_nivel/_tabla.html', {'montos': montos})
        else:
            data['form_is_valid'] = False
    else:
        form = MontoNivelForm(instance=monto)

    context = {'form': form}
    data['html_form'] = render_to_string('administracion/monto_nivel/_modal_form.html', context, request=request)
    return JsonResponse(data)


def eliminar_monto(request, pk):
    monto = get_object_or_404(MontoNivel, pk=pk)
    data = {}
    if request.method == 'POST':
        monto.delete()
        data['form_is_valid'] = True
        montos = MontoNivel.objects.select_related('ciclo', 'nivel').order_by('-ciclo__anio', 'nivel__nombre', '-fecha_vigencia_desde')
        data['html_list'] = render_to_string('administracion/monto_nivel/_tabla.html', {'montos': montos})
    else:
        context = {'monto': monto}
        data['html_form'] = render_to_string('administracion/monto_nivel/_modal_delete.html', context, request=request)
    return JsonResponse(data)


# ============================================================
# 🎓 BECAS Y BENEFICIOS
# ============================================================

def lista_becas(request):
    becas = Beca.objects.all().order_by('nombre')
    return render(request, 'administracion/beca/lista.html', {'becas': becas})


def crear_beca(request):
    data = {}
    if request.method == 'POST':
        form = BecaForm(request.POST)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            becas = Beca.objects.all().order_by('nombre')
            data['html_list'] = render_to_string('administracion/beca/_tabla.html', {'becas': becas})
        else:
            data['form_is_valid'] = False
    else:
        form = BecaForm()

    context = {'form': form}
    data['html_form'] = render_to_string('administracion/beca/_modal_form.html', context, request=request)
    return JsonResponse(data)


def editar_beca(request, pk):
    beca = get_object_or_404(Beca, pk=pk)
    data = {}
    if request.method == 'POST':
        form = BecaForm(request.POST, instance=beca)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            becas = Beca.objects.all().order_by('nombre')
            data['html_list'] = render_to_string('administracion/beca/_tabla.html', {'becas': becas})
        else:
            data['form_is_valid'] = False
    else:
        form = BecaForm(instance=beca)

    context = {'form': form}
    data['html_form'] = render_to_string('administracion/beca/_modal_form.html', context, request=request)
    return JsonResponse(data)


def eliminar_beca(request, pk):
    beca = get_object_or_404(Beca, pk=pk)
    data = {}
    if request.method == 'POST':
        beca.delete()
        data['form_is_valid'] = True
        becas = Beca.objects.all().order_by('nombre')
        data['html_list'] = render_to_string('administracion/beca/_tabla.html', {'becas': becas})
    else:
        context = {'beca': beca}
        data['html_form'] = render_to_string('administracion/beca/_modal_delete.html', context, request=request)
    return JsonResponse(data)


def inscribir_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    return render(request, 'administracion/inscripcion/inscribir_estudiante.html', {
        'estudiante': estudiante
    })

def lista_inscripciones_admin(request):
    return render(request, 'administracion/inscripcion/lista_inscripciones_admin.html')


def lista_cuotas(request):
    return render(request, 'administracion/secciones/lista_cuotas.html')

def lista_pagos(request):
    return render(request, 'administracion/secciones/lista_pagos.html')

