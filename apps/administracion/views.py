from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, FileResponse, JsonResponse
from django.template.loader import render_to_string
from apps.administracion.models import CicloLectivo, Nivel, Subnivel, MontoNivel, Beca, InscripcionAdministrativa, Cuota, Pago
from apps.administracion_alumnos.models import Estudiante, EstadoDocumentacion
from .forms import CicloLectivoForm, MontoNivelForm, BecaForm
from django.contrib import messages
from datetime import date
from django.db import models
from django.utils import timezone
from django.db.models import Q

def home(request):
    return render(request, 'home.html')

def home_administracion(request):
    return render(request, 'administracion/home_administracion.html')

# ==============================
# 🗓️ CICLOS
# ==============================
def lista_ciclos(request):
    ciclos = CicloLectivo.objects.all().order_by('-anio')
    return render(request, 'administracion/ciclo_lectivo/lista.html', {'ciclos': ciclos})


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
    montos = MontoNivel.objects.select_related('ciclo', 'nivel').order_by(
        '-ciclo__anio', 'nivel__nombre', '-fecha_vigencia_desde'
    )
    ciclos = CicloLectivo.objects.all().order_by('-anio')

    # 🔹 Año actual
    anio_actual = date.today().year

    # 🔹 Intentar obtener el ciclo del año actual (puede no existir)
    ciclo_actual = CicloLectivo.objects.filter(anio=anio_actual).first()

    return render(request, 'administracion/monto_nivel/lista.html', {
        'montos': montos,
        'ciclos': ciclos,
        'ciclo_actual': ciclo_actual,  # 🧩 lo pasamos al template
    })

def crear_monto(request):
    data = {}

    if request.method == 'POST':
        # 🔹 Siempre crear un form NUEVO con los datos del POST actual
        form = MontoNivelForm(request.POST)

        if form.is_valid():
            # ✅ Guardar el nuevo monto correctamente
            nuevo_monto = form.save(commit=False)

            # Si hay un monto activo anterior, lo cerramos
            anterior = MontoNivel.objects.filter(
                ciclo=nuevo_monto.ciclo,
                nivel=nuevo_monto.nivel,
                activo=True
            ).exclude(pk=nuevo_monto.pk).first()

            if anterior:
                anterior.activo = False
                anterior.fecha_vigencia_hasta = nuevo_monto.fecha_vigencia_desde
                anterior.save()

            # Guardar el nuevo monto
            nuevo_monto.save()

            # Actualizar cuotas pendientes desde la nueva vigencia
            inscripciones = InscripcionAdministrativa.objects.filter(
                ciclo=nuevo_monto.ciclo,
                nivel=nuevo_monto.nivel,
                activo=True
            )

            for ins in inscripciones:
                cuotas_restantes = ins.cuotas.filter(
                    estado='Pendiente',
                    mes__gte=nuevo_monto.fecha_vigencia_desde.month
                )
                for cuota in cuotas_restantes:
                    cuota.monto_original = nuevo_monto.monto_cuota
                    cuota.monto_final = nuevo_monto.monto_cuota - cuota.monto_descuento
                    cuota.save()

            # --- ✅ Respuesta exitosa ---
            data['form_is_valid'] = True
            montos = MontoNivel.objects.select_related('ciclo', 'nivel').order_by(
                '-ciclo__anio', 'nivel__nombre', '-fecha_vigencia_desde'
            )
            data['html_list'] = render_to_string(
                'administracion/monto_nivel/_tabla.html',
                {'montos': montos}
            )

        else:
            # --- ⚠️ Si hay errores, re-renderizamos el form con los mensajes ---
            data['form_is_valid'] = False
            data['html_form'] = render_to_string(
                'administracion/monto_nivel/_modal_form.html',
                {'form': form},
                request=request
            )

    else:
        # --- GET inicial (abrir modal vacío) ---
        form = MontoNivelForm()
        data['html_form'] = render_to_string(
            'administracion/monto_nivel/_modal_form.html',
            {'form': form},
            request=request
        )

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

def filtrar_montos(request):
    ciclo_id = request.GET.get('ciclo')
    activos = request.GET.get('activos')

    montos = MontoNivel.objects.all().select_related('nivel', 'ciclo')

    if ciclo_id:
        montos = montos.filter(ciclo_id=ciclo_id)
    if activos == '1':
        montos = montos.filter(activo=True)

    return render(request, 'administracion/monto_nivel/_tabla.html', {'montos': montos})


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
            # 👇 Renderizamos de nuevo el mismo form con errores
            data['html_form'] = render_to_string(
                'administracion/beca/_modal_form.html',
                {'form': form},
                request=request
            )
    else:
        form = BecaForm()
        data['html_form'] = render_to_string(
            'administracion/beca/_modal_form.html',
            {'form': form},
            request=request
        )

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
            data['html_form'] = render_to_string(
                'administracion/beca/_modal_form.html',
                {'form': form},
                request=request
            )
    else:
        form = BecaForm(instance=beca)
        data['html_form'] = render_to_string(
            'administracion/beca/_modal_form.html',
            {'form': form},
            request=request
        )

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


from django.db.models import Q

def estudiantes_becas_activas(request):
    """
    Muestra todos los estudiantes que tienen una beca asignada,
    permite cambiar o quitar la beca, y actualiza las cuotas pendientes.
    """
    # 🔹 Filtros recibidos
    ciclo_id = request.GET.get('ciclo')
    nivel_id = request.GET.get('nivel')
    beca_id = request.GET.get('beca')
    query = request.GET.get('q')

    # 🔹 Bases para los selects
    ciclos = CicloLectivo.objects.all().order_by('-anio')
    niveles = Nivel.objects.all().order_by('nombre')
    becas = Beca.objects.all().order_by('nombre')

    # 🔹 Traemos las inscripciones con beca (activa o inactiva)
    inscripciones = (
        InscripcionAdministrativa.objects
        .select_related('estudiante', 'beca', 'nivel', 'ciclo')
        .filter(beca__isnull=False)
    )

    # 🔹 Aplicar filtros si hay valores
    if ciclo_id:
        inscripciones = inscripciones.filter(ciclo_id=ciclo_id)
    if nivel_id:
        inscripciones = inscripciones.filter(nivel_id=nivel_id)
    if beca_id:
        inscripciones = inscripciones.filter(beca_id=beca_id)
    if query:
        inscripciones = inscripciones.filter(
            Q(estudiante__nombres_estudiante__icontains=query) |
            Q(estudiante__apellidos_estudiante__icontains=query)
        )

    # 🔹 Ordenar resultados
    inscripciones = inscripciones.order_by('-ciclo__anio', 'nivel__nombre', 'estudiante__apellidos_estudiante')

    # --- POST: si se está actualizando una beca ---
    if request.method == 'POST':
        inscripcion_id = request.POST.get('inscripcion_id')
        nueva_beca_id = request.POST.get('nueva_beca') or None
        accion = request.POST.get('accion')

        inscripcion = get_object_or_404(InscripcionAdministrativa, pk=inscripcion_id)

        # === Eliminar / Inactivar beca ===
        if accion == 'quitar':
            inscripcion.beca = None
            inscripcion.save()

            # 🔄 Recalcular cuotas pendientes sin descuento
            cuotas_pendientes = inscripcion.cuotas.filter(estado='Pendiente')
            for cuota in cuotas_pendientes:
                cuota.monto_descuento = 0
                cuota.monto_final = cuota.monto_original
                cuota.save()

            messages.success(request, f"❌ Se quitó la beca de {inscripcion.estudiante}.")
            return redirect('administracion:estudiantes_becas_activas')

        # === Cambiar por otra beca ===
        elif accion == 'cambiar' and nueva_beca_id:
            nueva_beca = get_object_or_404(Beca, pk=nueva_beca_id)
            inscripcion.beca = nueva_beca
            inscripcion.save()

            # 🔄 Recalcular descuentos de cuotas pendientes
            cuotas_pendientes = inscripcion.cuotas.filter(estado='Pendiente')
            for cuota in cuotas_pendientes:
                if nueva_beca.tipo == 'Porcentaje':
                    cuota.monto_descuento = cuota.monto_original * (nueva_beca.valor / 100)
                else:
                    cuota.monto_descuento = nueva_beca.valor
                cuota.monto_final = max(cuota.monto_original - cuota.monto_descuento, 0)
                cuota.save()

            messages.success(request, f"🔁 Se actualizó la beca de {inscripcion.estudiante} a {nueva_beca.nombre}.")
            return redirect('administracion:estudiantes_becas_activas')

    # 🔹 Contexto
    context = {
        'inscripciones': inscripciones,
        'becas': becas,
        'ciclos': ciclos,
        'niveles': niveles,
        'filtros': {
            'ciclo': ciclo_id,
            'nivel': nivel_id,
            'beca': beca_id,
            'q': query,
        },
    }
    return render(request, 'administracion/beca/estudiantes_activas.html', context)

def asignar_beca_general(request):
    # 🔹 Traemos todas las inscripciones activas sin beca asignada
    inscripciones = (
        InscripcionAdministrativa.objects
        .select_related('estudiante', 'nivel', 'ciclo')
        .filter(beca__isnull=True, activo=True)
        .order_by('-ciclo__anio', 'nivel__nombre', 'estudiante__apellidos_estudiante')
    )

    becas = Beca.objects.filter(activa=True).order_by('nombre')

    if request.method == 'POST':
        inscripcion_id = request.POST.get('inscripcion_id')
        beca_id = request.POST.get('beca_id')

        inscripcion = get_object_or_404(InscripcionAdministrativa, pk=inscripcion_id)
        beca = get_object_or_404(Beca, pk=beca_id)

        # Asignar la beca
        inscripcion.beca = beca
        inscripcion.save()

        # 🔄 Recalcular cuotas pendientes
        cuotas_pendientes = inscripcion.cuotas.filter(estado='Pendiente')
        for cuota in cuotas_pendientes:
            if beca.tipo == 'Porcentaje':
                cuota.monto_descuento = cuota.monto_original * (beca.valor / 100)
            else:
                cuota.monto_descuento = beca.valor
            cuota.monto_final = max(cuota.monto_original - cuota.monto_descuento, 0)
            cuota.save()

        messages.success(request, f"✅ Se asignó la beca {beca.nombre} a {inscripcion.estudiante}.")
        return redirect('administracion:estudiantes_becas_activas')

    context = {
        'inscripciones': inscripciones,
        'becas': becas,
    }
    return render(request, 'administracion/beca/asignar_beca_general.html', context)

def filtrar_becas(request):
    activos = request.GET.get('activos')

    # 🔹 Traemos todas las becas normalmente
    becas = Beca.objects.all().order_by('nombre')

    # 🔹 Filtramos si el check está marcado
    if activos == '1':
        becas = becas.filter(activa=True)

    return render(request, 'administracion/beca/_tabla.html', {'becas': becas})

from django.db.models import Q

def filtrar_estudiantes_becas(request):
    ciclo_id = request.GET.get('ciclo')
    nivel_id = request.GET.get('nivel')
    beca_id = request.GET.get('beca')
    query = request.GET.get('q')

    inscripciones = InscripcionAdministrativa.objects.select_related(
        'estudiante', 'ciclo', 'nivel', 'beca'
    )

    if ciclo_id:
        inscripciones = inscripciones.filter(ciclo_id=ciclo_id)
    if nivel_id:
        inscripciones = inscripciones.filter(nivel_id=nivel_id)
    if beca_id:
        inscripciones = inscripciones.filter(beca_id=beca_id)
    if query:
        inscripciones = inscripciones.filter(
            Q(estudiante__nombres_estudiante__icontains=query) |
            Q(estudiante__apellidos_estudiante__icontains=query)
        )

    return render(request, 'administracion/beca/_tabla_estudiantes.html', {
        'inscripciones': inscripciones,
        'becas': Beca.objects.all(),  # para el select dentro de cada fila
    })


# ============================================================
# 🎓 INSCRIPCION
# ============================================================

def inscribir_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    estado_doc = getattr(estudiante, 'estado_documentacion', None)

    # Verifica si puede inscribirse
    estado_actual = (estado_doc.estado.strip().lower() if estado_doc and estado_doc.estado else None)
    puede_inscribir = estado_actual == 'aprobado'

    # Datos para selects
    ciclos = CicloLectivo.objects.filter(activo=True)
    niveles = Nivel.objects.all()
    subniveles = Subnivel.objects.all()
    becas = Beca.objects.filter(activa=True)

    # 📩 Si envía el formulario (POST)
    if request.method == 'POST' and puede_inscribir:
        ciclo_id = request.POST.get('ciclo')
        nivel_id = request.POST.get('nivel')
        subnivel_id = request.POST.get('subnivel')
        turno = request.POST.get('turno')
        beca_id = request.POST.get('beca') or None
        observaciones = request.POST.get('observaciones', '')

        # Evita duplicados (ya inscripto en ese ciclo)
        if InscripcionAdministrativa.objects.filter(estudiante=estudiante, ciclo_id=ciclo_id).exists():
            messages.warning(request, "⚠️ Este estudiante ya está inscripto en el ciclo seleccionado.")
        else:
            # Busca el monto correspondiente al nivel y ciclo
            monto_registro = (
                MontoNivel.objects
                .filter(ciclo_id=ciclo_id, nivel_id=nivel_id, activo=True)
                .order_by('-fecha_vigencia_desde')
                .first()
            )

            if not monto_registro:
                messages.error(request, "❌ No se encontró un monto definido para este nivel y ciclo.")
            else:
                monto_inscripcion = monto_registro.monto_inscripcion

                # Crea la inscripción administrativa
                inscripcion = InscripcionAdministrativa.objects.create(
                    estudiante=estudiante,
                    ciclo_id=ciclo_id,
                    nivel_id=nivel_id,
                    subnivel_id=subnivel_id,
                    turno=turno,
                    monto_inscripcion=monto_inscripcion,
                    beca_id=beca_id,
                    observaciones=observaciones,
                    activo=True,
                )

                # ==============================
                # 📆 Crear automáticamente las 10 cuotas (Marzo a Diciembre)
                # ==============================
                anio_ciclo = inscripcion.ciclo.anio
                for mes in range(3, 13):  # marzo → diciembre
                    fecha_cuota = date(anio_ciclo, mes, 16)

                    # Buscar el monto vigente para ese mes
                    monto_vigente = (
                        MontoNivel.objects
                        .filter(
                            ciclo=inscripcion.ciclo,
                            nivel=inscripcion.nivel,
                            fecha_vigencia_desde__lte=fecha_cuota
                        )
                        .filter(
                            models.Q(fecha_vigencia_hasta__gte=fecha_cuota) |
                            models.Q(fecha_vigencia_hasta__isnull=True)
                        )
                        .order_by('-fecha_vigencia_desde')
                        .first()
                    )

                    if monto_vigente:
                        monto_original = monto_vigente.monto_cuota
                    else:
                        # Si no hay monto exacto para esa fecha, tomar el último del año
                        ultimo_monto = (
                            MontoNivel.objects
                            .filter(ciclo=inscripcion.ciclo, nivel=inscripcion.nivel)
                            .order_by('-fecha_vigencia_desde')
                            .first()
                        )
                        monto_original = ultimo_monto.monto_cuota if ultimo_monto else 0

                    # Calcular descuento por beca si aplica
                    monto_descuento = 0
                    if inscripcion.beca:
                        if inscripcion.beca.tipo == 'Porcentaje':
                            monto_descuento = monto_original * (inscripcion.beca.valor / 100)
                        else:
                            monto_descuento = inscripcion.beca.valor

                    monto_final = max(monto_original - monto_descuento, 0)

                    # Crear la cuota
                    Cuota.objects.create(
                        inscripcion=inscripcion,
                        mes=mes,
                        anio=anio_ciclo,
                        monto_original=monto_original,
                        monto_descuento=monto_descuento,
                        monto_final=monto_final,
                        fecha_vencimiento=fecha_cuota,
                        estado='Pendiente'
                    )

                # ✅ Mensaje final y redirección
                messages.success(request, f"✅ Inscripción y cuotas generadas correctamente ({inscripcion.nivel.nombre} - {anio_ciclo}).")
                return redirect('ver_datos_estudiante', pk=estudiante.id)

    context = {
        'estudiante': estudiante,
        'estado_doc': estado_doc,
        'puede_inscribir': puede_inscribir,
        'ciclos': ciclos,
        'niveles': niveles,
        'subniveles': subniveles,
        'becas': becas,
    }
    return render(request, 'administracion/inscripcion/inscribir_estudiante.html', context)

def registrar_pago(request, cuota_id):
    cuota = get_object_or_404(Cuota, pk=cuota_id)

    if request.method == 'POST':
        metodo = request.POST.get('metodo_pago')
        observaciones = request.POST.get('observaciones', '')

        pago = Pago.objects.create(
            metodo_pago=metodo,
            monto_total=cuota.monto_final,
            observaciones=observaciones,
            fecha_pago=timezone.now()
        )
        pago.cuotas_pagadas.add(cuota)

        cuota.estado = 'Pagada'
        cuota.fecha_pago = timezone.now().date()
        cuota.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return redirect('ver_datos_estudiante', pk=cuota.inscripcion.estudiante.id)
    
def deshacer_pago(request, cuota_id):
    cuota = get_object_or_404(Cuota, pk=cuota_id)

    if request.method == 'POST':
        # Buscar el pago asociado a esta cuota
        pago = Pago.objects.filter(cuotas_pagadas=cuota).first()
        if pago:
            # Si el pago solo tiene esta cuota → eliminarlo
            if pago.cuotas_pagadas.count() == 1:
                pago.delete()
            else:
                # Si compartía pago con otras cuotas, solo se quita la relación
                pago.cuotas_pagadas.remove(cuota)

        # Revertir el estado de la cuota
        cuota.estado = 'Pendiente'
        cuota.fecha_pago = None
        cuota.save()

        return redirect('ver_datos_estudiante', pk=cuota.inscripcion.estudiante.id)

