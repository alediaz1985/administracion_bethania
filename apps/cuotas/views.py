from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from apps.administracion_alumnos.models import Estudiante
from .models import CicloLectivo, Inscripcion, Cuota, Pago, MontosCicloLectivo, NivelCursado, SubNivelCursado, MedioPago, Estudiante, ComprobanteDrivePago
from .forms import MontosCicloLectivoForm, ActualizarMontosForm, ComprobanteDrivePagoForm
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from django.conf import settings
import os
from datetime import datetime, date
import locale
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP

# Habilitar Ciclo Lectivo
def habilitar_ciclo_lectivo(request):
    current_year = timezone.now().year

    if request.method == 'POST':
        año_lectivo = request.POST.get('año_lectivo')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        monto_inscripcion = request.POST.get('monto_inscripcion')
        monto_cuota = request.POST.get('monto_cuota')
        subnivel_cursado_ids = request.POST.getlist('subnivel_cursado')

        ciclos_existentes = MontosCicloLectivo.objects.filter(
            ciclo_lectivo__año_lectivo=año_lectivo,
            subnivel_cursado__id__in=subnivel_cursado_ids
        )

        if ciclos_existentes.exists():
            messages.error(request, "Ya existe un ciclo lectivo habilitado para el año seleccionado en algunos subniveles.")
            return redirect('cuotas:habilitar_ciclo_lectivo')

        subniveles_validos = SubNivelCursado.objects.filter(id__in=subnivel_cursado_ids)
        if not subniveles_validos.exists():
            messages.error(request, "No se han seleccionado subniveles válidos.")
            return redirect('cuotas:habilitar_ciclo_lectivo')

        ciclo_lectivo = CicloLectivo.objects.create(
            año_lectivo=año_lectivo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        for subnivel in subniveles_validos:
            MontosCicloLectivo.objects.create(
                ciclo_lectivo=ciclo_lectivo,
                subnivel_cursado=subnivel,
                monto_inscripcion=monto_inscripcion,
                monto_cuota_mensual=monto_cuota
            )

        messages.success(request, f'Ciclo lectivo {año_lectivo} habilitado correctamente.')
        return redirect('cuotas:habilitar_ciclo_lectivo')

    subniveles = SubNivelCursado.objects.all()
    return render(request, 'cuotas/habilitar_ciclo_lectivo.html', {
        'subniveles': subniveles,
        'current_year': current_year
    })


# Actualizar Montos
@user_passes_test(lambda u: u.is_superuser)
def actualizar_montos(request):
    ciclos_unicos = CicloLectivo.objects.all().distinct()
    subniveles = SubNivelCursado.objects.all()

    if request.method == 'POST':
        ciclo_id = request.POST.get('ciclo_lectivo_id')
        subnivel_id = request.POST.get('subnivel_cursado_id')
        monto_inscripcion = request.POST.get('monto_inscripcion')
        monto_cuota_mensual = request.POST.get('monto_cuota_mensual')

        ciclo_seleccionado = get_object_or_404(CicloLectivo, id=ciclo_id)
        subnivel_seleccionado = get_object_or_404(SubNivelCursado, id=subnivel_id)

        monto_existente = MontosCicloLectivo.objects.filter(
            ciclo_lectivo=ciclo_seleccionado,
            subnivel_cursado=subnivel_seleccionado
        ).first()

        if monto_existente:
            monto_existente.monto_inscripcion = monto_inscripcion
            monto_existente.monto_cuota_mensual = monto_cuota_mensual
            monto_existente.save()
            messages.success(request, f'Montos actualizados para {subnivel_seleccionado.nombre}.')
        else:
            MontosCicloLectivo.objects.create(
                ciclo_lectivo=ciclo_seleccionado,
                subnivel_cursado=subnivel_seleccionado,
                monto_inscripcion=monto_inscripcion,
                monto_cuota_mensual=monto_cuota_mensual
            )
            messages.success(request, f'Montos creados para {subnivel_seleccionado.nombre}.')

        return redirect('cuotas:actualizar_montos')

    return render(request, 'cuotas/actualizar_montos.html', {
        'ciclos': ciclos_unicos,
        'subniveles': subniveles,
    })

# Consultar Ciclo Lectivo
def consultar_ciclo_lectivo(request):
    montos = MontosCicloLectivo.objects.all().order_by('-fecha_actualizacion')

    ciclo_id = request.GET.get('ciclo_lectivo_id')
    ciclo_seleccionado = None
    if ciclo_id:
        ciclo_seleccionado = get_object_or_404(CicloLectivo, id=ciclo_id)

    return render(request, 'cuotas/consultar_ciclo_lectivo.html', {
        'montos': montos,
        'ciclo_seleccionado': ciclo_seleccionado,
    })

# Pago de Cuotas
# def pago_cuotas(request):
#     cuotas = Cuota.objects.filter(pagado=False)
#     medios_pago = MedioPago.objects.all()

#     if request.method == 'POST':
#         cuota_id = request.POST.get('cuota_id')
#         monto_pagado = request.POST.get('monto_pagado')
#         medio_pago_id = request.POST.get('medio_pago')

#         cuota = get_object_or_404(Cuota, id=cuota_id)
#         medio_pago = get_object_or_404(MedioPago, id=medio_pago_id)

#         Pago.objects.create(
#             cuota=cuota,
#             monto_pagado=monto_pagado,
#             medio_pago=medio_pago
#         )
#         cuota.pagado = True
#         cuota.save()
#         messages.success(request, f"Pago registrado correctamente para la cuota del mes {cuota.mes}.")

#     return render(request, 'cuotas/pago_cuotas.html', {
#         'cuotas': cuotas,
#         'medios_pago': medios_pago,
#     })

# Consultar Deudas
def consultar_deudas(request):
    estudiantes_deudores = Estudiante.objects.filter(inscripcion__cuota__pagado=False).distinct()
    return render(request, 'cuotas/consultar_deudas.html', {'estudiantes_deudores': estudiantes_deudores})

# Detalle de Deuda
def detalle_deuda(request, estudiante_id):
    cuotas = Cuota.objects.filter(inscripcion__cuil_alumno=estudiante_id, pagado=False)
    estudiante = get_object_or_404(Estudiante, cuil=estudiante_id)
    return render(request, 'cuotas/detalle_deuda.html', {'cuotas': cuotas, 'estudiante': estudiante})


def listar_montos(request):
    # Obtiene todos los montos de ciclo lectivo ordenados por fecha de actualización
    montos = MontosCicloLectivo.objects.all().order_by('-fecha_actualizacion')
    
    # Renderiza el template de listar montos
    return render(request, 'cuotas/listar_montos.html', {'montos': montos})

def generar_pdf_montos_view(request):
    # Nombre y ruta del archivo PDF
    pdf_path = os.path.join(settings.BASE_DIR, "montos_ciclo_lectivo.pdf")

    # Crear el PDF
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    elements = []
    styles = getSampleStyleSheet()

    # Título del PDF
    elements.append(Paragraph("Listado de Montos por Ciclo Lectivo", styles["Title"]))
    elements.append(Spacer(1, 0.5 * inch))

    # Obtener los datos
    montos = MontosCicloLectivo.objects.all()

    # Encabezados y datos
    data = [["Ciclo Lectivo", "Subnivel", "Inscripción", "Cuota Mensual", "Última Actualización"]]
    for monto in montos:
        data.append([
            monto.ciclo_lectivo.año_lectivo,
            monto.subnivel_cursado.nombre,
            f"${monto.monto_inscripcion}",
            f"${monto.monto_cuota_mensual}",
            monto.fecha_actualizacion.strftime("%d/%m/%Y"),
        ])

    # Crear tabla
    table = Table(data, colWidths=[2 * inch, 2 * inch, 1.5 * inch, 1.5 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Construir el documento
    doc.build(elements)

    # Devolver el archivo como respuesta
    return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename='montos_ciclo_lectivo.pdf')

def generar_pdf_montos_reportlab(request):
    # Crear un objeto HttpResponse para el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="montos_ciclo_lectivo_reportlab.pdf"'

    # Crear un objeto de lienzo de ReportLab
    p = canvas.Canvas(response, pagesize=A4)

    # Escribir el título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "Listado de Montos del Ciclo Lectivo")

    # Agregar los datos
    montos = MontosCicloLectivo.objects.all()
    y = 750  # Coordenada Y inicial
    for monto in montos:
        p.setFont("Helvetica", 12)
        p.drawString(100, y, f"Ciclo Lectivo: {monto.ciclo_lectivo.año_lectivo}")
        p.drawString(300, y, f"Subnivel: {monto.subnivel_cursado.nombre}")
        p.drawString(450, y, f"Inscripción: ${monto.monto_inscripcion}")
        y -= 20
        if y < 50:  # Si llega al final de la página, agrega una nueva página
            p.showPage()
            y = 800

    # Finalizar el lienzo
    p.showPage()
    p.save()

    return response

def listar_ciclos_lectivos(request):
    """
    Vista para listar todos los ciclos lectivos disponibles.
    """
    ciclos = CicloLectivo.objects.all().order_by('-año_lectivo')  # Ordenar por año lectivo de forma descendente
    return render(request, 'cuotas/listar_ciclos_lectivos.html', {'ciclos': ciclos})

def eliminar_ciclo_lectivo(request, año_lectivo):
    """
    Vista para eliminar un ciclo lectivo dado su año.
    """
    # Obtener el ciclo lectivo basado en el año
    ciclo_lectivo = get_object_or_404(CicloLectivo, año_lectivo=año_lectivo)

    if request.method == 'POST':
        # Elimina el ciclo lectivo
        ciclo_lectivo.delete()
        messages.success(request, f'El ciclo lectivo {año_lectivo} fue eliminado correctamente.')
        return redirect('cuotas:listar_ciclos_lectivos')  # Redirige a la lista de ciclos lectivos

    # Renderiza la página de confirmación antes de eliminar
    return render(request, 'cuotas/eliminar_ciclo_lectivo.html', {
        'ciclo_lectivo': ciclo_lectivo
    })

def listar_alumnos_por_ciclo_lectivo(request):
    """
    Vista para listar alumnos inscritos en un ciclo lectivo específico.
    """
    ciclos_lectivos = CicloLectivo.objects.all()
    alumnos = None
    ciclo_seleccionado = None

    if request.method == 'POST':
        ciclo_id = request.POST.get('ciclo_lectivo')
        ciclo_seleccionado = get_object_or_404(CicloLectivo, id=ciclo_id)
        alumnos = Inscripcion.objects.filter(ciclo_lectivo=ciclo_seleccionado).select_related('cuil_alumno')

    return render(request, 'cuotas/listar_alumnos.html', {
        'ciclos_lectivos': ciclos_lectivos,
        'alumnos': alumnos,
        'ciclo_seleccionado': ciclo_seleccionado,
    })

def generar_contrato_view(request, estudiante_id):
    # Establecer el idioma a español
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

    # Obtener el mes en español
    mes_en_espanol = datetime.now().strftime('%B')

    # Obtener los datos del estudiante
    estudiante = get_object_or_404(Estudiante, pk=estudiante_id)

    # Configuración del nombre del archivo
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d_%H-%M")
    pdf_path = f"Contrato - {estudiante.cuil_estudiante} - {fecha_hora_actual}.pdf"

    # Crear el PDF
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    # Metadata del PDF
    doc.title = "Contrato de Enseñanza Educativa"
    doc.author = "Hogar de Bethania"
    doc.subject = "Contrato personalizado para el estudiante"
    doc.creator = "Hogar de Bethania - Sistema de Gestión Educativa"

    styles = getSampleStyleSheet()
    elements = []

    # Título del contrato
    elements.append(Paragraph("CONTRATO DE ENSEÑANZA EDUCATIVA CICLO LECTIVO 2025", styles['Title']))
    elements.append(Spacer(1, 0.5 * inch))

    # Contenido del contrato (rellenado con datos del estudiante)
    contrato_texto = f"""
        En la ciudad de Presidencia Roque Sáenz Peña, Provincia del Chaco, a los {datetime.now().day} días del mes de {mes_en_espanol} del año {datetime.now().year}, 
        entre la UNIDAD EDUCATIVA DE GESTIÓN PRIVADA N° 82 “HOGAR DE BETHANIA” y los responsables del estudiante {estudiante.apellidos_responsable1} {estudiante.nombres_responsable1}, 
        D.N.I. N° {estudiante.dni_estudiante}, acuerdan suscribir el presente Contrato de Enseñanza, que es anual y que se regirá por las cláusulas que a continuación se detallan:
        
        PRIMERA: ...
        SEGUNDA: ...
    """
    elements.append(Paragraph(contrato_texto, styles['Normal']))

    # Firma de los responsables
    elements.append(Spacer(1, 0.5 * inch))
    firma_texto = f"""
        FIRMA DEL RESPONSABLE PARENTAL 1: ____________________________  DNI: {estudiante.dni_senores1}<br/>
        ACLARACIÓN: {estudiante.apellidos_responsable1} {estudiante.nombres_responsable1}<br/>
        FECHA: ____________________________
    """
    elements.append(Paragraph(firma_texto, styles['Normal']))

    # Generar el PDF
    doc.build(elements)

    # Devolver el PDF como respuesta
    return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename=f"Contrato_{estudiante.cuil_estudiante}.pdf")


def lista_fotos_estudiantes(request):
    estudiantes = Estudiante.objects.all()

    # Construir la URL de la foto para cada estudiante
    for estudiante in estudiantes:
        if estudiante.foto_estudiante:  # Si el estudiante tiene una foto asociada
            estudiante.image_url = os.path.join(
                settings.MEDIA_URL, 'administracion_alumnos', 'descargados', estudiante.foto_estudiante
            )
        else:  # Foto predeterminada si no tiene asociada
            estudiante.image_url = os.path.join(settings.STATIC_URL, 'images/default_profile.png')

    context = {
        'estudiantes': estudiantes,
    }
    return render(request, 'administracion_alumnos/lista_fotos_estudiantes.html', context)

def crear_comprobante_pago(request):
    if request.method == 'POST':
        form = ComprobanteDrivePagoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_comprobantes')
    else:
        form = ComprobanteDrivePagoForm()
    return render(request, 'cuotas/crear_comprobante_pago.html', {'form': form})

def listar_comprobantes(request):
    comprobantes = ComprobanteDrivePago.objects.all()
    return render(request, 'cuotas/listar_comprobantes.html', {'comprobantes': comprobantes})

def editar_comprobante_pago(request, pk):
    comprobante = get_object_or_404(ComprobanteDrivePago, pk=pk)
    if request.method == 'POST':
        form = ComprobanteDrivePagoForm(request.POST, instance=comprobante)
        if form.is_valid():
            form.save()
            return redirect('listar_comprobantes')
    else:
        form = ComprobanteDrivePagoForm(instance=comprobante)
    return render(request, 'cuotas/editar_comprobante_pago.html', {'form': form})

def eliminar_comprobante_pago(request, pk):
    comprobante = get_object_or_404(ComprobanteDrivePago, pk=pk)
    if request.method == 'POST':
        comprobante.delete()
        return redirect('listar_comprobantes')
    return render(request, 'cuotas/eliminar_comprobante_pago.html', {'comprobante': comprobante})

from django.shortcuts import render
from apps.administracion_alumnos.models import EstadoDocumentacion


# INSCRIPCION DE ESTUDIANTES FUNCIONANDO

# Función para obtener el subnivel solicitado
def obtener_subnivel(estudiante):
    subniveles = [
        ('Nivel Inicial de 3 años', estudiante.nivel_inicial3),
        ('Nivel Inicial de 4 años', estudiante.nivel_inicial4),
        ('Nivel Inicial de 5 años', estudiante.nivel_inicial5),
        ('Primario - 1er grado', estudiante.nivel_primario1),
        ('Primario - 2do grado', estudiante.nivel_primario2),
        ('Primario - 3er grado', estudiante.nivel_primario3),
        ('Primario - 4to grado', estudiante.nivel_primario4),
        ('Primario - 5to grado', estudiante.nivel_primario5),
        ('Primario - 6to grado', estudiante.nivel_primario6),
        ('Primario - 7mo grado', estudiante.nivel_primario7),
        ('Secundario - 1er año', estudiante.nivel_secundario1),
        ('Secundario - 2do año', estudiante.nivel_secundario2),
        ('Secundario - 3er año', estudiante.nivel_secundario3),
        ('Secundario - 4to año', estudiante.nivel_secundario4),
        ('Secundario - 5to año', estudiante.nivel_secundario5),
    ]

    for nombre, valor in subniveles:
        if valor:  # Si el subnivel tiene un valor (no está vacío ni es None)
            return nombre
    return "No especificado"  # Si no hay ningún valor, devuelve este texto

def buscar_estudiantes_aprobados(request):
    query = request.GET.get('q', '').strip()
    resultados = []
    subniveles = []  # Para almacenar los subniveles solicitados
    mensaje_documentacion_no_aprobada = None  # Mensaje para alumnos no aprobados
    mensaje_no_encontrado = None  # Mensaje para cuando no se encuentra ningún estudiante

    if query:
        # Primero buscamos estudiantes con documentación aprobada
        resultados_aprobados = EstadoDocumentacion.objects.filter(
            estado='aprobado',
            estudiante__cuil_estudiante__exact=query
        ).select_related('estudiante')

        if resultados_aprobados:
            # Si existen estudiantes con documentación aprobada
            resultados = resultados_aprobados
        else:
            # Si no hay aprobados, buscamos cualquier estudiante con ese CUIL
            resultados_existentes = EstadoDocumentacion.objects.filter(
                estudiante__cuil_estudiante__exact=query
            ).select_related('estudiante')

            if resultados_existentes:
                # Si el estudiante existe pero no tiene documentación aprobada
                resultados = resultados_existentes
                mensaje_documentacion_no_aprobada = "La documentación del alumno aún no ha sido aprobada."
            else:
                # Si no se encuentra ningún estudiante con ese CUIL
                resultados = []
                mensaje_no_encontrado = "No se encontró ningún estudiante con ese CUIL."

        # Obtener el subnivel solicitado por cada estudiante
        for estado in resultados:
            estudiante = estado.estudiante
            subnivel = obtener_subnivel(estudiante)
            subniveles.append(subnivel)
    
    ciclos_lectivos = CicloLectivo.objects.all().order_by('-año_lectivo')
    subniveles_disponibles = SubNivelCursado.objects.select_related('nivel_cursado').all()
    montos_disponibles = MontosCicloLectivo.objects.select_related('subnivel_cursado').all()

    if request.method == 'POST':
        ciclo_id = request.POST.get('ciclo')
        subnivel_id = request.POST.get('subnivel')
        monto_inscripcion = request.POST.get('monto_inscripcion')
        descuento_inscripcion = request.POST.get('descuento_inscripcion')
        pagada = request.POST.get('pagada') == 'on'

        # Recuperar el estudiante y otros datos
        estudiante = EstadoDocumentacion.objects.get(estudiante__cuil_estudiante=query).estudiante
        ciclo = CicloLectivo.objects.get(id=ciclo_id)
        subnivel = SubNivelCursado.objects.get(id=subnivel_id)

        monto_inscripcion = request.POST.get('monto_inscripcion', '').replace(',', '.')

        # Crear la inscripción
        inscripcion = Inscripcion.objects.create(
            cuil_alumno=estudiante,
            ciclo_lectivo=ciclo,
            subnivel_cursado=subnivel,
            monto_inscripcion=monto_inscripcion,
            descuento_inscripcion=descuento_inscripcion,
            pagada=pagada
        )

        # Obtener el monto mensual desde MontosCicloLectivo
        try:
            monto_mensual = MontosCicloLectivo.objects.get(
                ciclo_lectivo=ciclo,
                subnivel_cursado=subnivel
            ).monto_cuota_mensual
        except MontosCicloLectivo.DoesNotExist:
            monto_mensual = 0  # o lanzar error si querés

        # Crear las 10 cuotas mensuales
        for i in range(1, 11):
            mes_numero = i  # mes 1 a 10
            monto = monto_mensual
            total = monto  # si querés sumar interés más adelante, lo agregás acá
            fecha_vencimiento = ciclo.fecha_inicio + relativedelta(months=i - 1)

            # Por defecto no hay interés ni fuera de término
            interes = Decimal('0.00')
            fuera_de_termino = False

            # Si el mes y año coinciden con el actual y ya pasó el día 15
            hoy = date.today()

            # Si la fecha de vencimiento ya pasó o si estamos en el mes actual y ya pasó el día 15
            if fecha_vencimiento < hoy or (
                fecha_vencimiento.month == hoy.month and
                fecha_vencimiento.year == hoy.year and
                hoy.day > 15
            ):
                interes = monto * Decimal('0.10')
                total += interes
                fuera_de_termino = True

            # Crear la cuota con o sin interés
            Cuota.objects.create(
                inscripcion=inscripcion,
                mes=mes_numero,
                monto_cuota=monto,
                total_a_pagar=total,
                pagado=False,
                fecha_pago=None,
                fuera_de_termino=fuera_de_termino,
                interes_aplicado=interes
            )

        messages.success(request, f"El estudiante {estudiante.nombres_estudiante} {estudiante.apellidos_estudiante} ha sido inscrito correctamente.")
        return redirect('cuotas:inscribir_alumno')  # O donde redirijas después
    
    # 🔧 Agregá esto justo antes del return render
    sin_resultados = query and not resultados

    return render(request, 'cuotas/inscribir_alumno.html', {
        'resultados': zip(resultados, subniveles),  # Combinamos los resultados y subniveles
        'query': query,
        'mensaje_documentacion_no_aprobada': mensaje_documentacion_no_aprobada,  # Pasamos el mensaje
        'mensaje_no_encontrado': mensaje_no_encontrado,  # Pasamos el mensaje cuando no se encontró estudiante
        'ciclos_lectivos': ciclos_lectivos,
        'subniveles_disponibles': subniveles_disponibles,
        'montos_disponibles': montos_disponibles,
        'sin_resultados': sin_resultados,  # 🔧 Y esta línea en el contexto
    })

def buscar_cuotas_estudiante(request):
    estudiante = None
    inscripcion = None
    cuotas = []
    ciclo_seleccionado = None

    # Obtener todos los ciclos lectivos ordenados por año (del más reciente al más antiguo)
    ciclos_lectivos = CicloLectivo.objects.order_by('-año_lectivo')

    if request.method == 'POST':
        cuil = request.POST.get('cuil_estudiante')
        ciclo_id = request.POST.get('ciclo_lectivo')
        ciclo_seleccionado = int(ciclo_id) if ciclo_id else None

        estudiante = Estudiante.objects.filter(cuil_estudiante=cuil).first()
        if estudiante and ciclo_id:
            inscripcion = Inscripcion.objects.filter(cuil_alumno=estudiante, ciclo_lectivo_id=ciclo_id).first()
            if inscripcion:
                cuotas = Cuota.objects.filter(inscripcion=inscripcion).order_by('mes')
                hoy = date.today()

                for cuota in cuotas:
                    if not cuota.pagado:
                        fecha_vencimiento = inscripcion.ciclo_lectivo.fecha_inicio + relativedelta(months=cuota.mes - 1)

                        if fecha_vencimiento < hoy or (
                            fecha_vencimiento.month == hoy.month and
                            fecha_vencimiento.year == hoy.year and
                            hoy.day > 15
                        ):
                            interes = cuota.monto_cuota * Decimal('0.10')
                            
                            # Redondear a 2 decimales
                            interes = interes.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                            
                            cuota.total_a_pagar = (cuota.monto_cuota + interes).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                            cuota.fuera_de_termino = True
                            cuota.interes_aplicado = interes
                            cuota.save()  # Guardamos los cambios

    return render(request, 'cuotas/buscar_cuotas_estudiante.html', {
        'estudiante': estudiante,
        'inscripcion': inscripcion,
        'cuotas': cuotas,
        'ciclos_lectivos': ciclos_lectivos,
        'ciclo_seleccionado': ciclo_seleccionado,
    })

''' BUSCAR COMPROBANTES '''

from django.shortcuts import render
from .models import ComprobantePago
from django.db.models import Q
from .utils import descargar_comprobante_drive
import os
from django.db.models import Q
from googleapiclient.errors import HttpError

def buscar_comprobantes(request):
    comprobantes = None
    mensaje_error = None
    mensaje_exito = None

    # Valores del formulario de búsqueda
    cuil_alumno = request.GET.get('cuil_alumno', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')

    # Filtros para GET (búsqueda)
    if request.method == 'GET' and (cuil_alumno or fecha_desde or fecha_hasta):
        filtros = Q()
        if cuil_alumno:
            filtros &= Q(cuil_alumno=cuil_alumno)
        if fecha_desde and fecha_hasta:
            filtros &= Q(marca_temporal__range=[fecha_desde, fecha_hasta])
        elif fecha_desde:
            filtros &= Q(marca_temporal__gte=fecha_desde)
        elif fecha_hasta:
            filtros &= Q(marca_temporal__lte=fecha_hasta)

        comprobantes = ComprobantePago.objects.filter(filtros)

    # POST para descargar
    if request.method == 'POST' and 'descargar_todos' in request.POST:
        # En POST usamos todos los comprobantes
        comprobantes = ComprobantePago.objects.all()
        for comp in comprobantes:
            if comp.url_comprobante:
                try:
                    ruta_comprobante = descargar_comprobante_drive(comp.url_comprobante)
                    comp.ruta_local = ruta_comprobante  # Guardamos la ruta local en el modelo
                    comp.save()  # Si deseas almacenar la ruta local en el modelo de la base de datos
                except Exception as e:
                    print(f"Error al descargar {comp.url_comprobante}: {e}")
                    continue
        mensaje_exito = "¡Todos los comprobantes válidos fueron descargados!"

    return render(request, 'cuotas/buscar_comprobantes.html', {
        'comprobantes': comprobantes,
        'mensaje_exito': mensaje_exito,
        'mensaje_error': mensaje_error,
        'cuil_alumno': cuil_alumno,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    })


from django.shortcuts import render, get_object_or_404, redirect
from .models import Cuota, MedioPago, Pago
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect

from django.utils import timezone

def realizar_pago(request, cuota_id):
    cuota = get_object_or_404(Cuota, id=cuota_id)
    medios_pago = MedioPago.objects.all()

    if request.method == 'POST':
        medio_pago_id = request.POST.get('medio_pago')
        comentario = request.POST.get('comentario', '')
        medio_pago = get_object_or_404(MedioPago, id=medio_pago_id)

        pago = Pago.objects.create(
            cuota=cuota,
            monto_pagado=cuota.total_a_pagar,
            medio_pago=medio_pago,
            comentario=comentario
        )

        cuota.pagado = True
        cuota.fecha_pago = timezone.now()  # Asignar la fecha y hora actual
        cuota.save()

        messages.success(request, 'Pago registrado correctamente.')

        # Obtener el CUIL y ciclo lectivo desde la inscripción del estudiante
        estudiante = cuota.inscripcion.cuil_alumno
        ciclo_id = cuota.inscripcion.ciclo_lectivo.id

        url = reverse('cuotas:buscar_cuotas_estudiante')
        return HttpResponseRedirect(f'{url}?cuil={estudiante.cuil_estudiante}&ciclo_lectivo={ciclo_id}')

    return render(request, 'cuotas/realizar_pago.html', {
        'cuota': cuota,
        'medios_pago': medios_pago
    })


def deshacer_pago(request, cuota_id):
    cuota = get_object_or_404(Cuota, id=cuota_id)
    pago = Pago.objects.filter(cuota=cuota).first()

    if pago:
        pago.delete()
        cuota.pagado = False
        cuota.fecha_pago = None
        cuota.save()
        messages.success(request, 'El pago ha sido deshecho correctamente.')
    else:
        messages.warning(request, 'No se encontró un pago para esta cuota.')

    # Obtener el CUIL y ciclo lectivo desde la inscripción del estudiante
    estudiante = cuota.inscripcion.cuil_alumno
    ciclo_id = cuota.inscripcion.ciclo_lectivo.id

    url = reverse('cuotas:buscar_cuotas_estudiante')
    return HttpResponseRedirect(f'{url}?cuil={estudiante.cuil_estudiante}&ciclo_lectivo={ciclo_id}')