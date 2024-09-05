from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from apps.administracion_alumnos.models import Alumno
from apps.cuotas.models import Cuota, Inscripcion, DatosGlobales
from django.db import connection
from datetime import datetime

from datetime import date

#-------------------------------------------------------------------------

@login_required
def index(request):
    return render(request, 'cuotas/index.html')

@login_required
def cuotas_list(request):
    hoy = timezone.now()
    # Obtener el año lectivo activo
    año_lectivo_activo = DatosGlobales.objects.order_by('-año_lectivo').first()

    # Obtener todos los alumnos
    alumnos = Alumno.objects.all()
    meses = ["Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

    total_cuotas = []

    for alumno in alumnos:
        # Obtener la inscripción del alumno para el año lectivo activo
        inscripcion = Inscripcion.objects.filter(alumno=alumno, año_lectivo=año_lectivo_activo).first()
        if inscripcion:
            inscripcion_pagada = inscripcion.pagado
            monto_inscripcion = inscripcion.monto_inscripcion
        else:
            inscripcion_pagada = False
            monto_inscripcion = 0

        datos_alumno = {
            'cuil_alumno': alumno.cuil_alumno,
            'apellidos_alumno': alumno.apellidos_alumno,
            'nombres_alumno': alumno.nombres_alumno,
            'inscripcion_pagada': inscripcion_pagada,
            'inscripcion': monto_inscripcion,
            'meses': []
        }

        for mes in meses:
            cuota = Cuota.objects.filter(inscripcion=inscripcion, mes=mes).first()
            if cuota:
                cuota.calcular_interes()  # Asegúrate de calcular el interés si es necesario

                # Determinar el estado de la cuota
                if cuota.pagado:
                    estado = 'Pagado'
                elif hoy.month > meses.index(mes) + 3:  # Cambié la forma de calcular el estado
                    estado = 'Vencido'
                else:
                    estado = 'Activo'
                datos_alumno['meses'].append({
                    'nombre': mes,
                    'estado': estado,
                    'total': cuota.total_a_pagar
                })
            else:
                datos_alumno['meses'].append({
                    'nombre': mes,
                    'estado': 'Pendiente',
                    'total': 0
                })

        total_cuotas.append(datos_alumno)

    context = {
        'hoy': hoy,
        'alumnos': total_cuotas,
        'meses': meses
    }

    return render(request, 'cuotas/cuotas_list.html', context)

#-------------------------------------------------------------------------------

@login_required
def inscripcion(request):
    if request.method == 'POST':
        cuil_alumno = request.POST['cuil_alumno']
        año_lectivo_id = request.POST['año_lectivo']

        alumno = Alumno.objects.get(cuil_alumno=cuil_alumno)
        año_lectivo = DatosGlobales.objects.get(id=año_lectivo_id)

        # Crear inscripción
        inscripcion = Inscripcion.objects.create(
            alumno=alumno,
            año_lectivo=año_lectivo,
            monto_inscripcion=5000,  # Puedes ajustar el monto aquí
            pagado=True  # Ajustar según la lógica de pago
        )
        messages.success(request, f"Inscripción realizada para {alumno.nombres_alumno} {alumno.apellidos_alumno}")
        return redirect('inscripcion')

    alumnos = Alumno.objects.all()
    años_lectivos = DatosGlobales.objects.all()
    return render(request, 'cuotas/inscripcion.html', {'alumnos': alumnos, 'años_lectivos': años_lectivos})

@login_required
def habilitar_año_lectivo(request):
    if request.method == 'POST':
        año_lectivo = request.POST['año_lectivo']
        mes_inicio = request.POST['mes_inicio']
        mes_fin = request.POST['mes_fin']
        porcentaje_interes_mora = request.POST['porcentaje_interes_mora']

        # Crear un nuevo año lectivo
        DatosGlobales.objects.create(
            año_lectivo=año_lectivo,
            mes_inicio=mes_inicio,
            mes_fin=mes_fin,
            porcentaje_interes_mora=porcentaje_interes_mora
        )
        messages.success(request, f"Año lectivo {año_lectivo} habilitado.")
        return redirect('habilitar_año_lectivo')

    return render(request, 'cuotas/habilitar_año_lectivo.html')

@login_required
def crear_meses(request):
    if request.method == 'POST':
        año_lectivo_id = request.POST['año_lectivo']
        año_lectivo = DatosGlobales.objects.get(id=año_lectivo_id)
        meses = ["Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        for alumno in Alumno.objects.all():
            for mes in meses:
                Cuota.objects.get_or_create(
                    inscripcion=Inscripcion.objects.get(alumno=alumno, año_lectivo=año_lectivo), 
                    mes=mes, 
                    defaults={'monto': 1000, 'total_a_pagar': 1000}
                )

        messages.success(request, "Meses creados para todos los alumnos.")
        return redirect('crear_meses')

    años_lectivos = DatosGlobales.objects.all()
    return render(request, 'cuotas/crear_meses.html', {'años_lectivos': años_lectivos})

@login_required
def cobro_cuotas(request):
    if request.method == 'POST':
        cuil_alumno = request.POST.get('cuil_alumno')
        mes = request.POST.get('mes')
        hoy = timezone.now()

        try:
            cuota = Cuota.objects.get(inscripcion__alumno__cuil_alumno=cuil_alumno, mes=mes)

            if hoy.day > 15:
                cuota.fuera_de_termino = True
                cuota.interes_por_mora = cuota.monto * cuota.inscripcion.año_lectivo.porcentaje_interes_mora / 100
            else:
                cuota.fuera_de_termino = False
                cuota.interes_por_mora = 0

            cuota.pagado = True
            cuota.total_a_pagar = cuota.monto + cuota.interes_por_mora
            cuota.fecha_pago = hoy
            cuota.save()

            messages.success(request, f"La cuota del mes {mes} para {cuota.inscripcion.alumno.nombres_alumno} se pagó correctamente.")
        except Cuota.DoesNotExist:
            messages.error(request, "No se encontró la cuota para el alumno y mes seleccionados.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error al procesar el pago: {str(e)}")

        return redirect('cobro_cuotas')

    alumnos = Alumno.objects.all()
    meses = ["Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

    return render(request, 'cuotas/cobro_cuotas.html', {'alumnos': alumnos, 'meses': meses})

@login_required
def pagar_inscripcion(request):
    if request.method == 'POST':
        cuil_alumno = request.POST['cuil_alumno']
        alumno = Alumno.objects.get(cuil_alumno=cuil_alumno)
        año_lectivo = DatosGlobales.objects.order_by('-año_lectivo').first()

        inscripcion, created = Inscripcion.objects.get_or_create(
            alumno=alumno,
            año_lectivo=año_lectivo,
            defaults={'monto_inscripcion': año_lectivo.monto_inscripcion, 'pagado': True}
        )

        if not created and not inscripcion.pagado:
            inscripcion.pagado = True
            inscripcion.save()
            messages.success(request, "Inscripción pagada correctamente.")
        elif created:
            messages.success(request, "Inscripción creada y pagada correctamente.")
        else:
            messages.info(request, "La inscripción ya estaba pagada.")

        return redirect('cuotas_list')

    alumnos = Alumno.objects.all()
    return render(request, 'cuotas/pagar_inscripcion.html', {'alumnos': alumnos})

@login_required
def actualizar_monto_global_inscripcion(request):
    año_lectivo = DatosGlobales.objects.order_by('-año_lectivo').first()

    if request.method == 'POST':
        nuevo_monto = request.POST['nuevo_monto']
        año_lectivo.monto_inscripcion = nuevo_monto
        año_lectivo.save()
        messages.success(request, "El monto de la inscripción global ha sido actualizado.")

        return redirect('cuotas_list')

    return render(request, 'cuotas/actualizar_monto_global_inscripcion.html', {'año_lectivo': año_lectivo})

@login_required
def consulta_comprobantes(request):
    return render(request, 'cuotas/consulta_comprobantes.html')



def consultar_cuotas(request):
    anio = request.GET.get('anio')
    cuil = request.GET.get('cuil')
    cuotas = []

    if anio and cuil:
        with connection.cursor() as cursor:
            query = """
                SELECT mes, monto, fecha_pago, 
                       CASE 
                           WHEN pagado = 1 THEN 'Pagado' 
                           ELSE 'No Pagado' 
                       END AS estado
                FROM cuotas_cuota 
                WHERE inscripcion_id = (
                    SELECT id FROM cuotas_inscripcion 
                    WHERE cuil_alumno = %s AND año_lectivo_id = %s
                )
                ORDER BY mes ASC;
            """
            cursor.execute(query, [cuil, anio])
            cuotas = cursor.fetchall()

    return render(request, 'cuotas/consultar_cuotas.html', {'cuotas': cuotas})


def registrar_pago(request):
    mensaje = ""
    if request.method == 'POST':
        cuil = request.POST['cuil']
        mes = request.POST['mes']
        monto = request.POST['monto']
        fecha_pago = request.POST['fecha_pago']

        # Convertir la fecha de pago a un objeto datetime
        fecha_pago = datetime.strptime(fecha_pago, '%Y-%m-%d')

        with connection.cursor() as cursor:
            # Obtener la inscripción del alumno
            cursor.execute("""
                SELECT id FROM cuotas_inscripcion 
                WHERE cuil_alumno = %s
            """, [cuil])
            inscripcion = cursor.fetchone()

            if inscripcion:
                inscripcion_id = inscripcion[0]

                # Registrar el pago en la tabla cuotas_cuota
                cursor.execute("""
                    UPDATE cuotas_cuota
                    SET monto = %s, fecha_pago = %s, pagado = 1
                    WHERE inscripcion_id = %s AND mes = %s
                """, [monto, fecha_pago, inscripcion_id, mes])

                mensaje = "El pago se ha registrado exitosamente."
            else:
                mensaje = "No se encontró la inscripción del alumno."

    return render(request, 'cuotas/registrar_pago.html', {'mensaje': mensaje})


def estado_cuotas(request):
    # Consulta para obtener los datos de los alumnos, sus inscripciones y cuotas.
    with connection.cursor() as cursor:
        # Ejemplo de consulta para obtener alumnos e información sobre cuotas
        cursor.execute("""
            SELECT 
                a.cuil_alumno, 
                a.apellidos_alumno, 
                a.nombres_alumno, 
                ci.monto_inscripcion,
                ci.pagado AS inscripcion_pagada,
                c.mes,
                c.total_a_pagar AS total,
                CASE
                    WHEN c.pagado = 1 THEN 'Pagado'
                    WHEN c.fecha_pago IS NULL AND c.fuera_de_termino = 1 THEN 'Vencido'
                    WHEN c.fecha_pago IS NULL THEN 'Activo'
                    ELSE 'Pendiente'
                END AS estado
            FROM alumnos a
            LEFT JOIN cuotas_inscripcion ci ON a.cuil_alumno = ci.cuil_alumno
            LEFT JOIN cuotas_cuota c ON ci.id = c.inscripcion_id
            ORDER BY a.cuil_alumno, c.mes;
        """)
        
        resultados = cursor.fetchall()

    # Procesar los datos en una estructura adecuada para la plantilla
    alumnos = {}
    for fila in resultados:
        cuil_alumno = fila[0]
        if cuil_alumno not in alumnos:
            alumnos[cuil_alumno] = {
                'cuil_alumno': fila[0],
                'apellidos_alumno': fila[1],
                'nombres_alumno': fila[2],
                'inscripcion': fila[3],
                'inscripcion_pagada': fila[4],
                'meses': []
            }
        alumnos[cuil_alumno]['meses'].append({
            'nombre': fila[5],
            'total': fila[6],
            'estado': fila[7],
        })

    # Convertir el diccionario en una lista
    alumnos = list(alumnos.values())

    # Definir los nombres de los meses
    meses = [
        {'nombre': 'Enero'},
        {'nombre': 'Febrero'},
        {'nombre': 'Marzo'},
        {'nombre': 'Abril'},
        {'nombre': 'Mayo'},
        {'nombre': 'Junio'},
        {'nombre': 'Julio'},
        {'nombre': 'Agosto'},
        {'nombre': 'Septiembre'},
        {'nombre': 'Octubre'},
        {'nombre': 'Noviembre'},
        {'nombre': 'Diciembre'},
    ]

    contexto = {
        'hoy': date.today(),
        'alumnos': alumnos,
        'meses': meses,
    }

    return render(request, 'cuotas/estado_cuotas.html', contexto)