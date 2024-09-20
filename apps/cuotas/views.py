from django.shortcuts import render, redirect
from apps.administracion_alumnos.models import Alumno  
from .models import CicloLectivo, Inscripcion, Cuota, Pago
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

# Habilitar Ciclo Lectivo
def habilitar_ciclo_lectivo(request):
    error = None
    success = None
    current_year = timezone.now().year  # Obtener el año actual

    if request.method == 'POST':
        año_lectivo = request.POST.get('año_lectivo')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        monto_inscripcion = request.POST.get('monto_inscripcion')
        monto_cuota = request.POST.get('monto_cuota')

        # Validación: Verificar si los montos de inscripción y cuota están vacíos
        if not monto_inscripcion or not monto_cuota:
            error = 'El monto de inscripción y el monto de la cuota son obligatorios.'
        
        # Validación: Verificar que el año lectivo sea de 4 dígitos y sea igual al año actual o al siguiente
        elif not año_lectivo.isdigit() or len(año_lectivo) != 4 or int(año_lectivo) < current_year or int(año_lectivo) > current_year + 1:
            error = f"El año lectivo debe ser {current_year} o {current_year + 1}."
        
        # Validación: Verificar si el ciclo lectivo ya existe
        elif CicloLectivo.objects.filter(año_lectivo=año_lectivo).exists():
            error = f'El ciclo lectivo {año_lectivo} ya existe.'

        else:
            # Si todas las validaciones son exitosas, crear el ciclo lectivo
            CicloLectivo.objects.create(
                año_lectivo=año_lectivo,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                monto_inscripcion=monto_inscripcion,
                monto_cuota=monto_cuota
            )
            success = f'El ciclo lectivo {año_lectivo} ha sido habilitado correctamente.'
    
    # Renderizar el template con el contexto de éxito o error
    return render(request, 'cuotas/habilitar_ciclo_lectivo.html', {
        'error': error,
        'success': success
    })

#Consultar Ciclo Lectivo
def consultar_ciclo_lectivo(request):
    ciclos = CicloLectivo.objects.all()
    ciclo_seleccionado = None

    ciclo_id = request.GET.get('ciclo_lectivo_id')
    if ciclo_id:
        try:
            ciclo_seleccionado = CicloLectivo.objects.get(id=ciclo_id)
        except CicloLectivo.DoesNotExist:
            ciclo_seleccionado = None

    return render(request, 'cuotas/consultar_ciclo_lectivo.html', {
        'ciclos': ciclos,
        'ciclo_seleccionado': ciclo_seleccionado,
    })

# Inscripción de Alumnos
def inscribir_alumno(request):
    alumnos = Alumno.objects.all()  # Obtener todos los alumnos
    ciclos = CicloLectivo.objects.all()  # Obtener todos los ciclos lectivos

    # Inicializamos las variables para alumno, ciclo lectivo y monto de inscripción
    alumno_seleccionado = None
    ciclo_seleccionado = None
    monto_inscripcion = 0
    pagada = False  # Por defecto, no está pagada

    if request.method == 'POST':
        alumno_cuil = request.POST.get('alumno_id')
        ciclo_lectivo_id = request.POST.get('ciclo_lectivo')
        pagada = request.POST.get('pagada') == 'on'  # Verificar si el checkbox está marcado

        # Verificamos si se ha seleccionado un alumno
        if alumno_cuil:
            alumno_seleccionado = Alumno.objects.get(cuil_alumno=alumno_cuil)

        # Verificamos si se ha seleccionado un ciclo lectivo
        if ciclo_lectivo_id:
            try:
                ciclo_seleccionado = CicloLectivo.objects.get(id=ciclo_lectivo_id)
                monto_inscripcion = ciclo_seleccionado.monto_inscripcion  # Traer el monto de inscripción desde la base de datos
            except CicloLectivo.DoesNotExist:
                ciclo_seleccionado = None
                monto_inscripcion = 0

        # Crear la inscripción solo si se ha seleccionado un alumno y un ciclo lectivo
        if alumno_seleccionado and ciclo_seleccionado:
            # Verificar si el alumno ya está inscrito en ese ciclo
            if Inscripcion.objects.filter(cuil_alumno=alumno_seleccionado, ciclo_lectivo=ciclo_seleccionado).exists():
                # Redirigir a la página donde se indica que el alumno ya está inscrito
                messages.error(request, "El alumno ya está inscrito en este ciclo lectivo.")
                return render(request, 'cuotas/alumno_ya_inscrito.html', {
                    'alumno': alumno_seleccionado,
                    'ciclo': ciclo_seleccionado,
                })
            else:
                # Crear la inscripción
                Inscripcion.objects.create(
                    cuil_alumno=alumno_seleccionado,
                    ciclo_lectivo_id=ciclo_seleccionado.id,  # Usamos solo el ID del ciclo
                    monto_inscripcion=monto_inscripcion,
                    pagada=pagada
                )
                # Mostrar mensaje de éxito
                messages.success(request, f"El alumno {alumno_seleccionado.nombres_alumno} {alumno_seleccionado.apellidos_alumno} ha sido inscrito con éxito en el ciclo {ciclo_seleccionado.año_lectivo}.")
                return render(request, 'cuotas/inscripcion_exitosa.html', {
                    'alumno': alumno_seleccionado,
                    'ciclo': ciclo_seleccionado,
                    'monto_inscripcion': monto_inscripcion,
                    'pagada': pagada,
                })
        else:
            messages.error(request, "Debes seleccionar un alumno y un ciclo lectivo válido.")
    
    # Renderizamos el formulario si no es un POST
    return render(request, 'cuotas/inscribir_alumno.html', {
        'alumnos': alumnos,
        'ciclos': ciclos,
        'alumno_seleccionado': alumno_seleccionado,
        'ciclo_seleccionado': ciclo_seleccionado,
        'monto_inscripcion': monto_inscripcion,
        'pagada': pagada,
    })

# Pago de Cuotas
def pago_cuotas(request):
    if request.method == 'POST':
        cuota_id = request.POST.get('cuota_id')
        tutor_id = request.POST.get('tutor_id')
        monto_pagado = request.POST.get('monto_pagado')
        medio_pago = request.POST.get('medio_pago')

        # Obtener los objetos de tutor y cuota
        tutor = Tutor.objects.get(cuil_tutor=tutor_id)
        cuota = Cuota.objects.get(id=cuota_id)
        # Registrar el pago
        Pago.objects.create(cuota_id=cuota, tutor_id=tutor, monto_pagado=monto_pagado, medio_pago_id=medio_pago)

        # Marcar la cuota como pagada
        cuota.pagado = True
        cuota.save()

        return redirect('pago_cuotas')

    # Obtener las cuotas no pagadas y los tutores disponibles
    cuotas = Cuota.objects.filter(pagado=False)
    tutores = Tutor.objects.all()
    return render(request, 'cuotas/pago_cuotas.html', {'cuotas': cuotas, 'tutores': tutores})


# Consultar Deudas
def consultar_deudas(request):
    # Obtener los alumnos que tienen cuotas impagas
    alumnos_deudores = Alumno.objects.filter(inscripcion__cuota__pagado=False).distinct()
    return render(request, 'cuotas/consultar_deudas.html', {'alumnos_deudores': alumnos_deudores})


# Detalle de Deuda de un Alumno
def detalle_deuda(request, alumno_id):
    # Obtener las cuotas impagas del alumno
    cuotas = Cuota.objects.filter(inscripcion__cuil_alumno=alumno_id, pagado=False)
    alumno = Alumno.objects.get(cuil_alumno=alumno_id)
    return render(request, 'cuotas/detalle_deuda.html', {'cuotas': cuotas, 'alumno': alumno})


def actualizar_monto_inscripcion(request, ciclo_id):
    ciclo_lectivo = CicloLectivo.objects.get(id=ciclo_id)
    
    if request.method == 'POST':
        nuevo_monto = request.POST.get('monto_inscripcion')
        ciclo_lectivo.monto_inscripcion = nuevo_monto
        ciclo_lectivo.save()

        return redirect('lista_ciclos')

    return render(request, 'cuotas/actualizar_monto.html', {'ciclo': ciclo_lectivo})
