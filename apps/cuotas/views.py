from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from apps.administracion_alumnos.models import Alumno  
from .models import CicloLectivo, Inscripcion, Cuota, Pago, MontosCicloLectivo, NivelCursado, SubNivelCursado
from django.contrib.auth.decorators import user_passes_test
from .forms import MontosCicloLectivoForm
from .forms import ActualizarMontosForm  # Asegúrate de tener un formulario

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle


from django.http import FileResponse
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from .models import MontosCicloLectivo
from django.conf import settings


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
        subnivel_cursado_ids = request.POST.getlist('subnivel_cursado')  # Obtener los subniveles seleccionados

        # Verificar que no se habilite el mismo ciclo lectivo para los subniveles seleccionados
        ciclos_existentes = MontosCicloLectivo.objects.filter(
            ciclo_lectivo__año_lectivo=año_lectivo,
            subnivel_cursado__id__in=subnivel_cursado_ids
        )

        if ciclos_existentes.exists():
            messages.error(request, "Ya existe un ciclo lectivo habilitado para el año seleccionado en algunos de los subniveles.")
            return redirect('cuotas:habilitar_ciclo_lectivo')

        # Verificación de que los subniveles existen
        subniveles_validos = SubNivelCursado.objects.filter(id__in=subnivel_cursado_ids)
        if not subniveles_validos.exists():
            messages.error(request, "No se han seleccionado subniveles válidos.")
            return redirect('cuotas:habilitar_ciclo_lectivo')

        # Crear el ciclo lectivo
        ciclo_lectivo = CicloLectivo.objects.create(
            año_lectivo=año_lectivo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        # Crear montos para cada subnivel seleccionado
        for subnivel in subniveles_validos:
            MontosCicloLectivo.objects.create(
                ciclo_lectivo=ciclo_lectivo,
                subnivel_cursado=subnivel,
                monto_inscripcion=monto_inscripcion,
                monto_cuota_mensual=monto_cuota
            )

        success = f'Ciclo lectivo {año_lectivo} habilitado correctamente con montos para los subniveles seleccionados.'
        messages.success(request, success)
        return redirect('cuotas:habilitar_ciclo_lectivo')

    # Obtener los subniveles disponibles para la selección
    subniveles = SubNivelCursado.objects.all()

    # Pasar el año actual y el año siguiente a la plantilla
    return render(request, 'cuotas/habilitar_ciclo_lectivo.html', {
        'subniveles': subniveles,
        'current_year': current_year
    })

# Solo permitir que los administradores accedan
@user_passes_test(lambda u: u.is_superuser)
def actualizar_montos(request):
    # Obtener los ciclos únicos
    ciclos_unicos = CicloLectivo.objects.all().distinct()  # Obtener solo ciclos únicos
    subniveles = SubNivelCursado.objects.all()  # Obtener todos los subniveles

    if request.method == 'POST':
        ciclo_id = request.POST.get('ciclo_lectivo_id')
        subnivel_id = request.POST.get('subnivel_cursado_id')
        monto_inscripcion = request.POST.get('monto_inscripcion')
        monto_cuota_mensual = request.POST.get('monto_cuota_mensual')

        # Verificar que los IDs de ciclo y subnivel existan
        ciclo_seleccionado = get_object_or_404(CicloLectivo, id=ciclo_id)
        subnivel_seleccionado = get_object_or_404(SubNivelCursado, id=subnivel_id)

        # Verificar si ya existen montos para este ciclo y subnivel
        monto_existente = MontosCicloLectivo.objects.filter(ciclo_lectivo=ciclo_seleccionado, subnivel_cursado=subnivel_seleccionado).first()

        if monto_existente:
            # Actualizar montos existentes
            monto_existente.monto_inscripcion = monto_inscripcion
            monto_existente.monto_cuota_mensual = monto_cuota_mensual
            monto_existente.save()
            messages.success(request, f'Montos actualizados correctamente para el subnivel {subnivel_seleccionado.nombre}.')
        else:
            # Crear nuevos montos si no existen
            MontosCicloLectivo.objects.create(
                ciclo_lectivo=ciclo_seleccionado,
                subnivel_cursado=subnivel_seleccionado,
                monto_inscripcion=monto_inscripcion,
                monto_cuota_mensual=monto_cuota_mensual
            )
            messages.success(request, f'Montos creados correctamente para el subnivel {subnivel_seleccionado.nombre}.')

        return redirect('cuotas:actualizar_montos')

    return render(request, 'cuotas/actualizar_montos.html', {
        'ciclos': ciclos_unicos,
        'subniveles': subniveles,
    })

#OPCION 1
def generar_pdf_montos_reportlab(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="montos_ciclo_lectivo_reportlab.pdf"'

    # Crea el objeto PDF
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Título del PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, "Listado de Montos del Ciclo Lectivo")

    # Obtener los datos
    montos = MontosCicloLectivo.objects.all()

    # Encabezados
    data = [
        ['Ciclo Lectivo', 'Subnivel', 'Monto de Inscripción', 'Monto de Cuota Mensual', 'Fecha de Actualización']
    ]

    # Agregar los datos de los montos
    for monto in montos:
        data.append([
            str(monto.ciclo_lectivo.año_lectivo),
            monto.subnivel_cursado.nombre,
            f"${monto.monto_inscripcion}",
            f"${monto.monto_cuota_mensual}",
            monto.fecha_actualizacion.strftime("%d/%m/%Y")
        ])

    # Crear la tabla
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Ajustar la tabla en el PDF
    table.wrapOn(p, width, height)
    table.drawOn(p, 30, height - 300)  # Ajusta la posición de la tabla

    # Finaliza el PDF
    p.showPage()
    p.save()

    return response

def generar_pdf_montos_view(request):
    # Datos de la institución (puedes ajustarlos según necesites)
    datos_institucion = {
        "Nombre": "U.E.G.P. N°82",
        "Dirección": "Urquiza Nº 846, Pcia. Roque Sáenz Peña - Chaco",
        "Teléfono": "1122334455",
        "Email": "contacto@institucion.edu"
    }

    logo_path = os.path.join(settings.BASE_DIR, 'cuotas', 'static', 'cuotas', 'img', 'logo.png')
    pdf_path = generar_pdf_montos(datos_institucion, logo_path)
    return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename='listado_montos.pdf')

#OPCION 2
def generar_pdf_montos(datos_institucion, logo_path):
    # Nombre y ruta del archivo PDF
    pdf_path = "Listado_Montos_Ciclo_Lectivo.pdf"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d-%H%M")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=10, leftMargin=10, topMargin=10, bottomMargin=10)

    # Establecer los metadatos del documento
    doc.title = "Listado de Montos del Ciclo Lectivo"
    doc.author = "Fundación Hogar de Bethania U.E.G.P. N°82"

    # Estilos
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading2']
    styleH.alignment = 1  # Alinear en el centro

    elements = []

    # Insertar el logo
    try:
        if os.path.exists(logo_path):
            logo = Image(logo_path, 1 * inch, 1 * inch)
            elements.append(logo)
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        elements.append(Paragraph("Hogar de Bethania", getSampleStyleSheet()['Normal']))

    # Encabezado de la Institución
    elements.append(Spacer(1, 0.10 * inch))
    elements.append(Paragraph(datos_institucion["Nombre"], styles['Title']))
    elements.append(Paragraph(datos_institucion["Dirección"], styleN))
    elements.append(Paragraph(f"Teléfono: {datos_institucion['Teléfono']}", styleN))
    elements.append(Paragraph(f"Email: {datos_institucion['Email']}", styleN))

    # Título del listado
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("Listado de Montos del Ciclo Lectivo", styles['Title']))

    # Obtener los datos de los montos
    montos = MontosCicloLectivo.objects.all()

    # Datos a mostrar en la tabla
    datos_montos = [
        ["Ciclo Lectivo", "Subnivel", "Monto de Inscripción", "Monto de Cuota Mensual", "Fecha de Actualización"]
    ]

    # Agregar los datos de cada monto a la tabla
    for monto in montos:
        datos_montos.append([
            f"{monto.ciclo_lectivo.año_lectivo}",
            monto.subnivel_cursado.nombre,
            f"${monto.monto_inscripcion}",
            f"${monto.monto_cuota_mensual}",
            monto.fecha_actualizacion.strftime("%d/%m/%Y")
        ])

    # Crear la tabla
    tabla_montos = Table(datos_montos, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    tabla_montos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(Spacer(1, 0.5 * inch))
    elements.append(tabla_montos)

    # Generar el documento
    doc.build(elements)

    return pdf_path

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

# Consultar Ciclo Lectivo
def consultar_ciclo_lectivo(request):
    # Obtener todos los montos de ciclos lectivos ordenados por fecha de actualización
    montos_ciclos = MontosCicloLectivo.objects.all().order_by('ciclo_lectivo', 'subnivel_cursado', '-fecha_actualizacion')  

    # Filtrar los montos más recientes para cada combinación de ciclo lectivo y subnivel
    montos_filtrados = {}
    for monto in montos_ciclos:
        key = (monto.ciclo_lectivo, monto.subnivel_cursado)
        if key not in montos_filtrados:
            montos_filtrados[key] = monto

    montos_ciclos_unicos = list(montos_filtrados.values())

    ciclo_seleccionado = None
    montos_subniveles = None

    ciclo_id = request.GET.get('ciclo_lectivo_id')
    if ciclo_id:
        try:
            ciclo_seleccionado = CicloLectivo.objects.get(id=ciclo_id)
            # Obtener los montos más recientes por ciclo lectivo y subnivel seleccionados
            montos_subniveles = MontosCicloLectivo.objects.filter(ciclo_lectivo=ciclo_seleccionado).order_by('-fecha_actualizacion').first()  # Obtener solo el más reciente
        except CicloLectivo.DoesNotExist:
            ciclo_seleccionado = None

    return render(request, 'cuotas/consultar_ciclo_lectivo.html', {
        'montos_ciclos': montos_ciclos_unicos,  # Pasar los montos de los ciclos únicos para el dropdown
        'ciclo_seleccionado': ciclo_seleccionado,
        'montos_subniveles': [montos_subniveles] if montos_subniveles else [],  # Asegurarse de que solo sea el último monto
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

# Función para eliminar un ciclo lectivo
def eliminar_ciclo_lectivo(request, año_lectivo):
    # Intentamos obtener el ciclo lectivo por año
    ciclo_lectivo = get_object_or_404(CicloLectivo, año_lectivo=año_lectivo)
    
    # Si es una solicitud POST (confirmación de eliminación)
    if request.method == 'POST':
        ciclo_lectivo.delete()
        success = f'El ciclo lectivo {año_lectivo} ha sido eliminado correctamente.'
        return redirect('listar_ciclos_lectivos')  # Redirige a una página donde se listan los ciclos lectivos
    
    # Si no es POST, mostramos una página de confirmación de eliminación
    return render(request, 'cuotas/eliminar_ciclo_lectivo.html', {
        'ciclo_lectivo': ciclo_lectivo
    })


# Finciones para Listar

def listar_ciclos_lectivos(request):
    ciclos = CicloLectivo.objects.all()
    return render(request, 'cuotas/listar_ciclos_lectivos.html', {'ciclos': ciclos})

def listar_alumnos_por_ciclo_lectivo(request):
    ciclos = CicloLectivo.objects.all()
    alumnos = None
    ciclo_seleccionado = None

    if request.method == 'POST':
        ciclo_id = request.POST.get('ciclo_lectivo')
        ciclo_seleccionado = CicloLectivo.objects.get(id=ciclo_id)
        alumnos = Alumno.objects.filter(inscripcion__ciclo_lectivo=ciclo_seleccionado)

    return render(request, 'cuotas/listar_alumnos.html', {
        'ciclos': ciclos,
        'alumnos': alumnos,
        'ciclo_seleccionado': ciclo_seleccionado,
    })


def listar_montos(request):
    # Obtiene todos los montos de ciclo lectivo ordenados por fecha de actualización
    montos = MontosCicloLectivo.objects.all().order_by('-fecha_actualizacion')
    
    # Renderiza el template de listar montos
    return render(request, 'cuotas/listar_montos.html', {'montos': montos})