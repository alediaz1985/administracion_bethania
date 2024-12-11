import re  
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, FileResponse
from .models import Alumno
from .forms import AlumnoForm
from django.contrib import messages
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from io import BytesIO
from django.conf import settings
import os
from datetime import datetime
from django.utils import timezone


def alumno_list(request):
    alumnos = Alumno.objects.all()
    if not alumnos:
        return HttpResponse("No se encontraron alumnos en la base de datos.")
    return render(request, 'administracion_alumnos/alumno_list.html', {'alumnos': alumnos})

def alumno_detail(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    return render(request, 'administracion_alumnos/alumno_detail.html', {'alumno': alumno})

def ver_datos_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    campos_alumno = {field.name: getattr(alumno, field.name) for field in alumno._meta.fields}
    return render(request, 'administracion_alumnos/ver_datos_alumno.html', {'alumno': alumno, 'campos_alumno': campos_alumno})

def alumno_edit(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    if request.method == "POST":
        form = AlumnoForm(request.POST, request.FILES, instance=alumno)
        if form.is_valid():
            form.save()
            messages.success(request, 'Los cambios han sido guardados correctamente.')
            return redirect('alumno_detail', pk=alumno.pk)
    else:
        form = AlumnoForm(instance=alumno)
    return render(request, 'administracion_alumnos/alumno_edit.html', {'form': form})

def alumno_delete(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    if request.method == "POST":
        alumno.delete()
        messages.success(request, 'Alumno eliminado correctamente.')
        return redirect('consultar_alumno')
    return render(request, 'administracion_alumnos/alumno_confirm_delete.html', {'alumno': alumno})

def test_connection(request):
    try:
        alumnos = Alumno.objects.all()
        if not alumnos:
            return HttpResponse("No se encontraron alumnos en la base de datos.")
        
        response_content = "<h1>Lista de Alumnos</h1><ul>"
        for alumno in alumnos:
            response_content += f"<li>{alumno.nombres} {alumno.apellidos}</li>"
        response_content += "</ul>"
        
        return HttpResponse(response_content)
    except Exception as e:
        return HttpResponse(f"Error al conectar a la base de datos: {e}")

def test_view(request):
    alumnos = Alumno.objects.all()
    output = "Lista de Alumnos:<br>"
    for alumno in alumnos:
        output += f"{alumno.id}: {alumno.nombres} {alumno.apellidos} - {alumno.correo_electronico}<br>"
    return HttpResponse(output)


def consultar_alumno(request):
    alumno = None
    error = None

    if request.method == "POST":
        cuil = request.POST.get('cuil')
        # Verifica si el CUIL solo contiene dígitos
        if not cuil or not re.fullmatch(r'\d+', cuil):
            error = 'El CUIL debe contener solo números y no puede estar vacío.'
        else:
            try:
                alumno = Alumno.objects.get(cuil_alumno=cuil)
            except Alumno.DoesNotExist:
                error = 'No se encontró un alumno con ese CUIL.'

    return render(request, 'administracion_alumnos/consultar_alumno.html', {'alumno': alumno, 'error': error})

def registrar_alumno(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            alumno = form.save(commit=False)
            alumno.fecha_registro = timezone.localtime(timezone.now())  # Obtener la fecha y hora actual con el timezone configurado
            alumno.save()
            messages.success(request, 'Alumno registrado correctamente.')
            return redirect('alumno_list')
        else:
            messages.error(request, 'Por favor, corrija los errores a continuación.')
    else:
        form = AlumnoForm()
    return render(request, 'administracion_alumnos/registrar_alumno.html', {'form': form})

# Función para generar PDF de un alumno
def generar_pdf_alumno_view(request, alumno_id):
    alumno = get_object_or_404(Alumno, pk=alumno_id)
    datos_institucion = {
        "Nombre": "U.E.G.P. N°82",
        "Dirección": "Urquiza Nº 846, Pcia. Roque Sáenz Peña - Chaco",
        "Teléfono": "1122334455",
        "Email": "contacto@institucion.edu"
    }
    logo_path = os.path.join(settings.BASE_DIR, 'alumnos', 'static', 'alumnos', 'img', 'logo.png')
    pdf_path = generar_pdf_alumno(alumno, datos_institucion, logo_path)
    return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename='ficha_alumno.pdf')

def generar_pdf_alumno(alumno, datos_institucion, logo_path):
    pdf_path = "Ficha del Alumno.pdf"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d-%H%M")
    nombre_archivo = f"{fecha_hora_actual}.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=10, leftMargin=10, topMargin=10, bottomMargin=10)

    # Establecer los metadatos del documento
    doc.title = "Ficha Alumno - {}".format(fecha_hora_actual)
    doc.author = "Fundación Hogar de Bethania U.E.G.P. N°82"

    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading2']
    styleH.alignment = 1  # Center alignment for headings
    
    elements = []

    try:
        if os.path.exists(logo_path):
            logo = Image(logo_path, 1*inch, 1*inch)
            elements.append(logo)
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        elements.append(Paragraph("Hogar de Bethania", getSampleStyleSheet()['Normal']))

    elements.append(Spacer(1, 0.10*inch))
    elements.append(Paragraph(datos_institucion["Nombre"], styles['Title']))
    elements.append(Paragraph(datos_institucion["Dirección"], styleN))
    elements.append(Paragraph(f"Teléfono: {datos_institucion['Teléfono']}", styleN))
    elements.append(Paragraph(f"Email: {datos_institucion['Email']}", styleN))

    elements.append(Paragraph("Ficha del Alumno", styles['Title']))
    elements.append(Paragraph("Datos del Alumno", styleH))
    datos_alumno = [
        ["Nombre Completo", f"{alumno.nombres_alumno} {alumno.apellidos_alumno}"],
        ["Fecha de Nacimiento", alumno.fecha_nacimiento_alumno],
        ["CUIL", alumno.cuil_alumno],
        ["Género", alumno.genero_alumno],
        ["Domicilio", alumno.domicilio_residencia_alumno],
        ["Localidad", alumno.localidad_residencia_alumno],
        ["Provincia", alumno.provincia_residencia_alumno],
        ["Código Postal", alumno.codigo_postal_alumno],
        ["Teléfono", alumno.numero_telefonico_alumno],
        ["Localidad de Nacimiento", alumno.localidad_nacimiento_alumno],
        ["Provincia de Nacimiento", alumno.provincia_nacimiento_alumno],
        ["Nacionalidad", alumno.nacionalidad_alumno],
        ["Nivel Cursado", alumno.nivel_cursado_alumno],
        ["Ingreso", alumno.ingreso_alumno],
        ["Medicamento", alumno.medicamento_alumno],
        ["Alergia", alumno.alergia_alumno],
        ["Alergico a Medicamento", alumno.alergico_medicamento_alumno],
        ["Condición Médica", alumno.condicion_medica_alumno]
    ]
    tabla_alumno = Table(datos_alumno, colWidths=[2*inch, 4*inch], hAlign='CENTER')
    tabla_alumno.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(tabla_alumno)
    elements.append(Spacer(1, 0.5*inch))

    elements.append(Paragraph("Datos del Tutor", styleH))
    datos_tutor = [
        ["Nombre Completo", alumno.apellido_nombre_tutor],
        ["CUIL", alumno.cuil_tutor],
        ["Teléfono", alumno.telefono_tutor],
        ["Domicilio", alumno.domicilio_tutor],
        ["Localidad", alumno.localidad_tutor],
        ["Provincia", alumno.provincia_tutor],
        ["Código Postal", alumno.codigo_postal_tutor]
    ]
    tabla_tutor = Table(datos_tutor, colWidths=[2*inch, 4*inch], hAlign='CENTER')
    tabla_tutor.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(tabla_tutor)
    elements.append(Spacer(1, 0.5*inch))

    doc.build(elements)
    return pdf_path

def generar_pdf_lista_alumnos_view(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="lista_alumnos.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=15, bottomMargin=30)

    # Establecer los metadatos del documento
    doc.title = "Lista de Alumnos"
    doc.author = "Fundación Hogar de Bethania U.E.G.P. N°82"

    elements = []

    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    try:
        if os.path.exists(logo_path):
            logo = Image(logo_path, 1*inch, 1*inch)
            elements.append(logo)
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        elements.append(Paragraph("Hogar de Bethania", getSampleStyleSheet()['Normal']))

    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph("Lista de Alumnos", getSampleStyleSheet()['Title']))

    # Obtener los alumnos ordenados por nivel y luego alfabéticamente por apellido
    alumnos = Alumno.objects.all().order_by('nivel_cursado_alumno', 'apellidos_alumno')

    current_level = None
    for alumno in alumnos:
        if alumno.nivel_cursado_alumno != current_level:
            if current_level is not None:
                # Añadir la tabla de alumnos del nivel anterior
                tabla = Table(data, colWidths=[2*inch, 2*inch, 2*inch, 2*inch], hAlign='CENTER')
                tabla.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.black),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(tabla)
                elements.append(Spacer(1, 0.5*inch))
            
            current_level = alumno.nivel_cursado_alumno
            elements.append(Paragraph(f"Nivel: {current_level}", getSampleStyleSheet()['Heading2']))
            data = [["CUIL", "Apellido", "Nombre", "Teléfono"]]

        data.append([
            alumno.cuil_alumno,
            alumno.apellidos_alumno,
            alumno.nombres_alumno,
            alumno.numero_telefonico_alumno,
        ])

    # Añadir la última tabla de alumnos
    if data:
        tabla = Table(data, colWidths=[2*inch, 2*inch, 2*inch, 2*inch], hAlign='CENTER')
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(tabla)

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def estudiante_edit(request, pk):
    """
    Vista para editar la información de un alumno.
    """
    alumno = get_object_or_404(Estudiante, pk=pk)
    if request.method == "POST":
        form = EstudianteForm(request.POST, instance=alumno)
        if form.is_valid():
            form.save()
            return redirect('estudiante_detail', pk=alumno.pk)  # Redirige al detalle del alumno
    else:
        form = EstudianteForm(instance=alumno)
    return render(request, 'administracion_alumnos/estudiante_edit.html', {'form': form})

def estudiante_delete(request, pk):
    """
    Vista para eliminar un alumno.
    """
    alumno = get_object_or_404(Estudiante, pk=pk)
    if request.method == "POST":
        alumno.delete()
        return redirect(reverse('estudiante_list'))  # Redirige a la lista de alumnos
    return render(request, 'administracion_alumnos/alumno_confirm_delete.html', {'alumno': alumno})


def estudiante_delete(request, pk):
    """
    Vista para eliminar un alumno.
    """
    alumno = get_object_or_404(Estudiante, pk=pk)
    if request.method == "POST":
        alumno.delete()
        return redirect(reverse('estudiante_list'))  # Redirige a la lista de alumnos
    return render(request, 'administracion_alumnos/alumno_confirm_delete.html', {'alumno': alumno})

def estudiante_consultar(request):
    estudiante = None
    error = None

    if request.method == "POST":
        cuil = request.POST.get('cuil')
        if not cuil or not re.fullmatch(r'\d+', cuil):
            error = 'El CUIL debe contener solo números y no puede estar vacío.'
        else:
            try:
                # Obtén el registro más reciente para el CUIL
                estudiante = (
                    Estudiante.objects.filter(cuil_estudiante=cuil)
                    .order_by('-marca_temporal')  # Ordena por la última marca temporal
                    .first()  # Obtén el primer registro
                )
                if not estudiante:
                    error = 'No se encontró un estudiante con ese CUIL.'
            except Exception as e:
                error = f'Ocurrió un error inesperado: {e}'

    return render(
        request,
        'administracion_alumnos/estudiante_consultar.html',
        {'estudiante': estudiante, 'error': error}
    )

import locale
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from .models import Estudiante


"""
 estudiante = get_object_or_404(Estudiante, pk=estudiante_id)
    datos_institucion = {
        "Nombre": "U.E.G.P. N°82",
        "Dirección": "Urquiza 768 / 846 Presidencia Roque Sáenz Peña.",
        "Teléfono": "0364-4423041 / 0364-4436798",
        "Email": "contacto@hdebethania.edu.ar"
    }
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    pdf_path = generar_pdf_estudiante(estudiante, datos_institucion, logo_path)

    # Incluir el CUIL, fecha y hora en el nombre del archivo
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"Ficha del Estudiante - {estudiante.cuil_estudiante} - {fecha_hora_actual}.pdf"

    return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename=filename)
"""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from datetime import datetime
import locale
import os
from django.conf import settings

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle

from reportlab.lib.enums import TA_JUSTIFY

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.enums import TA_CENTER

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

    # Ruta del logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')

    # Crear el PDF
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=20,
        leftMargin=25,
        topMargin=10,
        bottomMargin=10,
    )

    # Metadata del PDF
    doc.title = "Contrato de Enseñanza Educativa"
    doc.author = "Hogar de Bethania"
    doc.subject = "Contrato personalizado para el estudiante"
    doc.creator = "Hogar de Bethania - Sistema de Gestión Educativa"

    styles = getSampleStyleSheet()
    elements = []

    # Agregar el logo al PDF
    #elements.append(Spacer(1, 0.5 * inch))  # Espaciado inicial
    logo = Image(logo_path)
    logo.drawHeight = 0.5 * inch  # Altura del logo
    logo.drawWidth = 0.5 * inch  # Ancho del logo
    logo.hAlign = 'CENTER'  # Centrar el logo
    elements.append(logo)
    #elements.append(Spacer(1, 0.5 * inch))  # Espaciado debajo del logo

    # Crear un estilo personalizado
    custom_title_style = ParagraphStyle(
        'CustomTitle',  # Nombre del estilo
        fontName='Times-Bold',  # Times New Roman en negrita
        fontSize=16,  # Tamaño de la fuente
        leading=22,  # Espaciado entre líneas
        alignment=1,  # Centrar el texto
        textColor=colors.white,  # Color del texto
        backColor=colors.navy,  # Color de fondo
        padding=10,  # Margen interno
    )
    elements.append(Spacer(1, 0.3 * inch))
    # Usar el estilo personalizado Título del contrato
    elements.append(Paragraph("CONTRATO DE ENSEÑANZA EDUCATIVA CICLO LECTIVO 2025", custom_title_style))

    elements.append(Spacer(1, 0.2 * inch))

    # Obtener el nivel de enseñanza actual desde la base de datos
    nivel_ensenanza_texto = "Nivel de Enseñanza: " + "  " + estudiante.nivel_ensenanza.strip().upper()
   
    # Agregarlo al contenido del PDF
    elements.append(Paragraph(nivel_ensenanza_texto, styles['Normal']))

    elements.append(Spacer(1, 0.1 * inch))

    contrato_style = ParagraphStyle(
    'ContratoStyle',
    fontName='Times-Roman',
    fontSize=10,
    leading=14,  # Espaciado entre líneas
    alignment=TA_JUSTIFY,  # Justificar el texto
    #leftIndent=30,  # Sangría en todos los párrafos
    firstLineIndent=25,  # Sangría solo para la primera línea
)
    # Contenido del contrato (rellenado con datos del estudiante)
    contrato_texto = f"""
        En la ciudad de Presidencia Roque Sáenz Peña, Provincia del Chaco, a los {datetime.now().day} días del mes de {mes_en_espanol} del año {datetime.now().year}, 
        entre la UNIDAD EDUCATIVA DE GESTIÓN PRIVADA N° 82 “HOGAR DE BETHANIA”, con domicilio legal en URQUIZA N° 768 localidad
        de Presidencia Roque Sáenz Peña, provincia del Chaco, representada en este acto por el Sr. Moreno, Rodolfo Jonatan, D.N.I. N° 27.482.233
        en su carácter de Representante Legal, en adelante denominada LA INSTITUCIÓN, por una parte; y por la otra, los
        señores(1) {estudiante.senores1} D.N.I.: {estudiante.dni_senores1} y (2) {estudiante.senores2} D.N.I.: {estudiante.dni_senores2} con domicilio en {estudiante.domicilios_senores} y domicilio especial
        electrónico {estudiante.domicilio_especial_electronico} actúan en su propio nombre y en representación del estudiante, menor de edad, {estudiante.actuan_nombres_estudiante} D.N.I. N° {estudiante.dni_acutan_estudiante}, domiciliado
        realmente en {estudiante.domicilio_actuan_estudiante},en adelante denominado LOS RESPONSABLES,
        acuerdan suscribir el presente Contrato de Enseñanza, que es anual y que se regirá por las cláusulas que a continuación se detallan:<br/>
        PRIMERA: LOS RESPONSABLES reconocen que LA INSTITUCIÓN es una Unidad Educativa de Gestión Privada, cuyo objetivo es
        promover la formación integral del estudiante, capacitándolo para que a partir de la apropiación de los distintos saberes, y de una línea de
        principios y valores cristianos que se desprenden de la Biblia, logre construir su propio proyecto de vida.- <br/>
        SEGUNDA: LOS RESPONSABLES y el estudiante1, al solicitar la inscripción del menor (reserva de vacante), eligen libremente dentro
        de las opciones que ofrece el medio, contratar los servicios educativos de LA INSTITUCIÓN durante el ciclo lectivo 2025 con arreglo a
        las condiciones y lineamientos establecidos en el presente Contrato. En consecuencia, declaran haber leído, aceptado y adherido al Ideario
        Institucional (I.I), el Proyecto Educativo, Reglamento Interno (R.I.) y Acuerdo de Convivencia (A.C.), asumiendo como propios los
        objetivos educativos, la identidad cristiana y los principios morales de LA INSTITUCIÓN.- <br/>
        TERCERA: LOS RESPONSABLES se comprometen personalmente a cumplir y a hacer cumplir al estudiante el Reglamento Interno (R.I.),
        Acuerdo de Convivencia (A.C.) y el compromiso educativo que suscriben, coadyuvando con LA INSTITUCIÓN en su calidad de
        integrantes de la Comunidad Educativa para llevar adelante el I.I. y el Proyecto Educativo (el cual incluye el uso de la plataforma digital
        como herramienta de acompañamiento en el proceso enseñanza y aprendizaje) al que adhieren, procurando mantener sus principios sin que
        se pierda la causa y los objetivos originarios.- <br/>
        CUARTA: LA INSTITUCIÓN prestará a los estudiantes sus servicios educativos de acuerdo a los planes de estudios oficiales que aplica
        la misma, y demás actividades extracurriculares que sus Directivos resuelvan implementar, cumpliendo en un todo las obligaciones a su
        cargo establecidas en el presente contrato.
        Entendiéndose a la educación como una tarea compartida por LOS RESPONSABLES e INSTITUCIÓN EDUCATIVA, cuya finalidad es
        llevar adelante acciones educativas de manera conjunta; es necesario mantener entre ambas partes la cooperación, colaboración, confianza,
        y la buena fe, que una educación responsable exige en su proceder. Cuando dichos principios no estén presentes en la tarea educativa, es
        imposible llevar delante de manera eficaz.- <br/>
        QUINTA: En este acto LA INSTITUCIÓN pone en conocimiento de LOS RESPONSABLES el contenido del I.I., el R.I. y el A.C., no
        pudiendo en adelante alegar desconocimiento de la reglamentación y/o espíritu de los términos que rigen la relación y convivencia de las
        partes.- <br/>
        SEXTA: En contraprestación por la enseñanza que LA INSTITUCIÓN brindará al alumno, LOS RESPONSABLES se comprometen a
        abonar un arancel anual dividido en diez cuotas mensuales y consecutivas, pagaderas por adelantado desde el día que se emite la factura
        hasta la fecha que les será comunicado juntamente con el valor del arancel mensual. Asimismo, corresponde abonar como condición previa
        para el ingreso del alumno a LA INSTITUCIÓN la suma de pesos CIEN MIL ($100.000 .-) en concepto de matrícula (reserva de vacante).
        Cabe aclarar que nuestra Unidad Educativa es de Gestión Privada y recibe del Estado Provincial el aporte para los sueldos de los docentes
        de la Planta Funcional únicamente, pero toda otra realidad de LA INSTITUCIÓN: docentes no subvencionados por el Estado, personal
        auxiliar de sala y/o grado, de Inglés, Educación Física y Artística, Educación Cristiana, psicopedagogo, maestranzas, mantenimiento,
        plataforma educativa, seguros, cobertura médica asistencial, seguridad y otros servicios, se cubre con los aranceles por enseñanza que
        abonan las familias. De allí que cada familia al elegir esta INSTITUCIÓN para sus hijos, debe asumir el compromiso de abonar los aranceles
        por enseñanza conforme lo detallado a continuación.
        Del analisis que actualmente vive nuestro país, el cual es de resultado incierto, hemos acordado para el CICLO ESCOLAR 2025 un arancel
        inicial por enseñanza según el nivel: <br/>
        - Nivel Inicial = CIENTO CINCO MIL ($105.000). <br/>
        - Nivel Primario = NOVENTA MIL ($90.000). <br/>
        - Nivel Secundario = SETENTA Y NUEVE MIL ($79.000). <br/>
        Para tener la posibilidad de re-inscribirse, que no es automático, deberá tener la totalidad de las cuotas canceladas y realizarse en la fecha
        definida por la institución para cada nivel. Por lo tanto, para la inscripción (a través de la presentación de la solicitud de vacante) deberá
        presentar constancia de libre deuda a la fecha y recibo de pago. De no ser así, la vacante dejará de estar reservada.
        Los aranceles por enseñanza incluyen además de la propuesta educativa los siguientes servicios: enseñanza de idioma, educación cristiana,
        entre otros.<br/>
        No incluyen: excursiones, salidas didácticas, jornadas educativas, campamentos, pileta, congresos, Fiesta de la Familia, Fiesta de la
        Educación Física, viajes de estudio, salidas especiales; como así también útiles escolares, libreta de calificaciones , inasistencias e informe
        pedagógico, material de uso didáctico exclusivo para el alumno, comidas de ningún tipo, entre otros.
        El costo de las actividades antes mencionadas no están incluidas en los aranceles. Por lo tanto, se condicionará la asistencia de los alumnos
        a cualquier actividad curricular o extracurricular, al pago en tiempo y forma de los importes que se fijen para su realización. LOS
        RESPONSABLES prestarán su colaboración y aceptación manifestada a través del presente Contrato de Enseñanza. Esto implica convalidar
        todas las acciones y decisiones necesarias para el logro de los objetivos escolares planteados y la entrega de la documentación necesaria
        para cada actividad.- <br/>
        SEPTIMA: ARANCELES POR ENSEÑANZA, lineamientos:<br/>
        a) La matrícula o reserva de vacante se abona al momento de la firma del presente contrato, entregándose el recibo correspondiente
        al pagador en formato digital vía email.<br/>
        b) La Matrícula o reserva de vacante podrá ser desistida por LOS RESPONSABLES del alumno, en caso de mediar razones de
        fuerza mayor, dando lugar a la devolución del importe abonado por tal concepto a valores históricos si tal decisión es comunicada
        fehacientemente al establecimiento antes del 31/12/2024. Con posterioridad a dicha fecha, así como en los casos en que el
        desistimiento obedezca a causas imputables a los responsables y/o alumnos, los importes abonados por tal concepto no serán
        reintegrados. Sin excepción.<br/>
        c) LA INSTITUCIÓN se reserva la facultad de incrementar unilateralmente el monto de las cuotas teniendo en cuenta la evolución
        general de la economía del país y si se produjeren modificaciones en los regímenes laborales y/o previsionales e/o impositivos
        que por su incidencia pudieran comprometer el normal cumplimiento del servicio educativo, conforme a la normativa vigente.
        d) Los aranceles por enseñanza fijados, son estimados teniendo en cuenta el receso escolar invernal, feriados, etc.-<br/>
        (1) Sólo en el caso de los alumnos mayores de 13 años.<br/>
        e) La escuela se reserva el derecho de cobrar la totalidad de las cuotas, ya que las mismas son indivisibles, es decir son
        independientes de la cantidad de días de asistencia que se registre de cada alumno en cuestión, sea por causas particulares o
        propias del calendario escolar y/o caso fortuito o fuerza mayor (por disposición de las autoridades nacionales y/o provinciales
        y/o municipales decretaran por motivo expreso el no dictado de clases presenciales), ello por cuanto la contraprestación de la
        INSTITUCIÓN EDUCATIVA es indivisible, ya que los aranceles se establecen considerando toda la enseñanza a impartir en
        el año 2025 para todo el plan de continuidad pedagógica, ya sea presencial o virtual o ambos conjuntamente, siendo la obligación
        de pago única aun cuando pueda ser cancelada en cuotas mensuales. Por esta razón, bajo ninguna circunstancia podrán LOS
        RESPONSABLES solicitar ni pretender que se les exima de cumplir una parte cualquiera de la obligación de pago que se asume.<br/>
        f) En caso que LOS RESPONSABLES soliciten la recisión del presente contrato antes de finalizar el ciclo lectivo, deberán
        comunicarlo por escrito a la Dirección de la escuela exclusivamente, siempre y cuando la cuota correspondiente al mes de la
        solicitud se encuentre al día, sin obligación de abonar el importe total del arancel anual. En caso de NO AVISAR, el sistema
        continuará facturando las cuotas hasta que se haga efectiva dicha notificación.<br/>
        g) Cuando un alumno se retire durante el mes de noviembre, cualquiera fuera la fecha, deberá abonar la cuota Nº10
        indefectiblemente. -<br/>
        h) Cuando el ingreso a la escuela se realice en un determinado mes, en cualquier época del año (por alguna circunstancia
        extraordinaria), se deberá abonar íntegramente tanto la matrícula como el mes en curso cualquiera fuera la fecha de ingreso.
        i) Los estudiantes que perdieran la regularidad por causa de inasistencias tendrán derecho a solicitar reincorporación; para lo cuál
        deberán: presentar la solicitud de reincorporación, libre deuda y abonar el arancel correspondiente (Nivel Secundario).<br/>
        j) En caso de que en el ciclo lectivo se incumplan con algunos de los aspectos referenciados en el R.I. y el A.C., especialmente en
        el caso del retiro del alumno fuera de los horarios establecidos, LA INSTITUCIÓN determinará, para los casos repetidos y
        constantes, el pago de una cuota adicional a fin de solventar los gastos que ocasione la contratación de un personal para el
        cuidado del alumno. Dicha facultad se sustenta en el deber de colaboración mutua entre escuela-familia, ya que como institución
        no se cuenta con recursos humanos para dicha función específica, no obstante institucionalmente somos conscientes del deber
        de protección de la vida, salud y seguridad del alumno. La determinación de dicha cuota adicional le será notificada
        previamente.-<br/>
        OCTAVA: Las Diez (10) cuotas en que se divide el arancel por enseñanza anual se abonarán mensualmente en el domicilio de LA
        INSTITUCIÓN por los medios de pago que oportunamente se informen; la primera en el mes de marzo, y por adelantado, del uno (1) al
        diez (10) de cada mes, entregándose el recibo correspondiente al pagador.-<br/>
        NOVENA: Mora en el pago de aranceles: se prevé que para los supuestos de atraso en el pago del arancel, la mora se producirá de pleno
        derecho sin necesidad de interpelación judicial o extrajudicial alguna; queda facultada LA INSTITUCIÓN a exigir a LOS
        RESPONSABLES PARENTALES Y/U OTRO RESPONSABLE DE PAGO el abono de los recargos por mora que devengará un interés
        equivalente a la tasa pasiva del BNA, sobre el valor factura, como así también las costas de recupero, a cuenta de su abono.- <br/>
        DÉCIMA: La falta de pago de dos (2) cuotas mensuales, continuas o alteradas, hará incurrir en mora de pleno derecho sin necesidad de
        interpelación judicial o extrajudicial alguna, quedando facultada LA INSTITUCIÓN para exigir a LOS RESPONSABLES, su pago con
        más tasa pasiva judicial.
        Sólo se podrá acreditar el pago de las cuotas mediante la exhibición de los recibos emitidos por la administración del establecimiento. -
        * En caso de realizar transferencia bancaria deberá presentar o enviar vía email el comprobante emitido por la entidad, así luego el área de administración podrá realizar la
        acreditación correspondiente.<br/>
        DÉCIMA PRIMERA: En el caso de incumplimiento en el pago de dos (2) cuotas mensuales, de los aranceles pactados entre las partes o
        ruptura contractual, las mismas convienen de común acuerdo que las deudas serán remitidas automáticamente a un estudio jurídico y podrán
        cobrarse por el mecanismo de la preparación de vía ejecutiva, constituyendo el presente contrato suficiente título ejecutivo, pudiendo
        dirigirse la acción judicial en forma conjunta, separada, o indistinta contra cualquiera de los RESPONSABLES PARENTALES Y/U OTRO
        RESPONSABLE DE PAGO.-<br/>
        DÉCIMA SEGUNDA: LA INSTITUCIÓN se reserva en cualquier época, el ejercicio pleno de la permanencia del estudiante, pudiendo
        separar del establecimiento a aquellos que cometan faltas graves y/o incumplan con lo acordado en el I.I., R.I. y A.C. Como así también,
        la admisión del estudiante en ciclos lectivos anteriores no implicará la continuidad con posterioridad, no existiendo por parte de LA
        INSTITUCIÓN ni del RESPONSABLE obligación alguna de renovar el presente contrato.-<br/>
        DÉCIMA TERCERA: LA INSTITUCIÓN no renovará la matrícula, entre otros, en los siguientes casos:<br/>
        a) No existan vacantes disponibles y/o el cupo este cubierto.<br/>
        b) El estudiante que haya evidenciado problemas reiterados de disciplina y/o integración con la Comunidad Educativa.<br/>
        c) Hayan violado las normas de la Institución y/o sus objetivos, sin evidenciar cambios de actitud.<br/>
        d) Hayan atentado en forma grave contra el buen nombre y prestigio de la Institución.<br/>
        e) Necesitando reincorporarse el estudiante por inasistencias, su comportamiento integral y su rendimiento no sean aptos conforme
        las bases y principios del I.I., R.I., A.C., y Proyecto Educativo de LA INSTITUCIÓN.-<br/>
        f) El estudiante haya incumplido el cronograma arancelario de LA INSTITUCIÓN al momento de la reserva de vacante.<br/>
        g) En los demás casos contemplados expresa o tácitamente en el R.I. y A.C. de LA INSTITUCIÓN. -<br/>
        * A fin de no vulnerar el derecho de aprender, el Establecimiento asegura que en caso de uso del Derecho de Admisión, se comunicará con la antelación necesaria a efectos
        de posibilitar la matriculación del estudiante en otra Institución Educativa.<br/>
        DÉCIMA CUARTA: LOS RESPONSABLES se obligan a mantener actualizado desde el ingreso hasta el egreso todos los datos de
        identidad propios del alumno, que resulten ser atributos de la personalidad, así como también aquellos que por su especificidad resulten
        indispensables para su inscripción, reinscripción y mantenimiento de la condición de alumno, conforme a las disposiciones vigentes. El
        ocultamiento de información será considerado falta grave en el presente contrato. Asimismo, LOS RESPONSABLES deberán mantener
        una regular comunicación con LA INSTITUCIÓN, notificándose y haciéndole saber a ésta de todas las novedades que resulten necesarias,
        mediante el mecanismo de comunicación que determine la misma. Como así también deberán asistir al establecimiento las veces que sean
        citados en el día y hora establecidos.-<br/>
        DÉCIMA QUINTA: LOS RESPONSABLES se obligan a controlar que el alumno no ingrese al establecimiento con objetos, sustancias
        y/o elementos ajenos o innecesarios para la enseñanza que se imparta, o los que pudieren ser -cierta o potencialmente- perjudiciales, tanto
        para la salud del alumno como para la de cualquiera de los demás miembros de la comunidad educativa; facultando por este acto al
        establecimiento a proceder al retiro de dichos objetos.-<br/>
        DÉCIMA SEXTA: Dado que nuestra institución es una escuela común (no especial) e integradora, con capacidad limitada en cuanto a la
        posibilidad de integración, tanto en recursos humanos como edilicios, por tanto, LOS RESPONSABLES se comprometen a informar en el
        proceso de reserva de vacante, de cualquier necesidad educativa especial, a fin de evaluar si LA INSTITUCIÓN posee los recursos
        necesarios para lograr eficazmente la inclusión o integración. En caso de no ser brindada en el mencionado tiempo o por ocultamiento de
        información, LA INSTITUCIÓN no puede responsabilizarse que dicha integración puede ser llevada a cabo con éxito; reservándose la
        institución educativa el derecho de rescindir el presente contrato. LA INSTITUCIÓN considera como factor determinante para el abordaje
        y continuidad del proceso de inclusión, el beneficio mutuo a efectos de que sea una experiencia cabalmente enriquecedora y el resultado
        de un trabajo colaborativo y cooperativo con la familia.<br/>
        DÉCIMA SÉPTIMA: LOS RESPONSABLES se comprometen a abonar en concepto de resarcimiento las sumas dinerarias que, resulten
        pertinentes por todo daño que pudiere generar de manera voluntaria y/o por su culpa o negligencia el alumno, tanto en los bienes propios
        del establecimiento, como en la integridad psíquica o física de los miembros de la comunidad educativa, en su persona o pertenencias.. <br/>
        DÉCIMA OCTAVA: Se deja expresa constancia que LA INSTITUCIÓN no participa ni adhiere a ningún evento que sea ajeno a la tarea
        educativa o aquellas no organizadas por ella misma. A título meramente enunciativo se mencionan: viajes de egresados, fiestas de fin de
        curso, veladas, rifas o sorteos de cualquier índole que se realicen a tal fin, etc. En caso que LOS RESPONSABLES decidan por sí o
        mediante terceros la realización de alguno de estos eventos, harán constar fehacientemente por escrito que las contrataciones que realicen
        en tales ocasiones las asumen a título personal, debiendo deslindar expresamente de toda responsabilidad al Establecimiento Educativo.<br/>
        DÉCIMA NOVENA: EL RESPONSABLE se obliga a completar todos y cada uno de los documentos emitidos por LA INSTITUCION,
        como así también los referentes a aptos físicos y calendarios de vacunación completos.<br/>
        VIGÉSIMA: A los efectos del presente contrato las partes fijan domicilio legal y especial electrónico en los lugares ut-supra mencionados,
        donde serán válidas todas las comunicaciones y/o notificaciones judiciales y extrajudiciales, y subsistirán aun cuando no se encuentren o
        residan allí. LOS RESPONSABLES, en consecuencia, se compromete a comunicar a LA INSTITUCIÓN por medio fehaciente la
        modificación de su domicilio dentro de las 48hs de producido.-<br/>
        VIGÉSIMA PRIMERA: Quienes suscriben el presente contrato en carácter de RESPONSABLES actúan en forma solidaria e
        ilimitadamente, constituyéndose en recíprocos fiadores y principales pagadores entre sí, con renuncia a los beneficios de excusión y
        división.-<br/>
        VIGÉSIMA SEGUNDA: A todos los efectos del presente contrato las partes se someten voluntariamente a los tribunales ordinarios,
        correspondientes al domicilio de LA INSTITUCION, renunciando a cualquier otro fuero o jurisdicción que pudiere corresponder. -<br/>
        <br/>
        Se firma un ejemplar a modo CONTRATO DE ADHESION en la ciudad de Presidencia Roque Sáenz Peña, Chaco a los {datetime.now().day} días del mes de {mes_en_espanol} del año {datetime.now().year}.-

        """

    elements.append(Paragraph(contrato_texto, contrato_style))

    # Firma de los responsables
    elements.append(Spacer(1, 0.2 * inch))

    # Definir el estilo para las firmas
    firma_style = ParagraphStyle(
        'FirmaStyle',
        fontName='Times-Roman',
        fontSize=9,  # Tamaño de la fuente
        leading=11,  # Espaciado entre líneas
        alignment=TA_CENTER,  # Alineación centrada
        spaceBefore=0,  # Espaciado antes del texto
        spaceAfter=0,  # Espaciado después del texto
    )

    # Datos para la tabla de firmas (convertidos a Paragraphs)
    firma_datos = [
        [
            Paragraph(f"""
            FIRMA DEL RESPONSABLE PARENTAL 1:<br/><br/><br/>
            ____________________________<br/>
            DNI: {estudiante.dni_senores1}<br/>
            ACLARACIÓN: {estudiante.apellidos_responsable1} {estudiante.nombres_responsable1}<br/>
            FECHA: ____________________________
            """, firma_style),
            Paragraph(f"""
            FIRMA DEL RESPONSABLE PARENTAL 2:<br/><br/><br/>
            ____________________________<br/>
            DNI: {estudiante.dni_senores2}<br/>
            ACLARACIÓN: {estudiante.apellidos_responsable2} {estudiante.nombres_responsable2}<br/>
            FECHA: ____________________________
            """, firma_style),
        ],
        [
            Paragraph(f"""
            FIRMA DEL RESPONSABLE PARENTAL 1:<br/><br/><br/>
            ____________________________<br/>
            DNI: {estudiante.dni_senores1}<br/>
            ACLARACIÓN: {estudiante.apellidos_responsable1} {estudiante.nombres_responsable1}<br/>
            FECHA: ____________________________
            """, firma_style),
            Paragraph(f"""
            FIRMA DEL RESPONSABLE PARENTAL 2:<br/><br/><br/>
            ____________________________<br/>
            DNI: {estudiante.dni_senores2}<br/>
            ACLARACIÓN: {estudiante.apellidos_responsable2} {estudiante.nombres_responsable2}<br/>
            FECHA: ____________________________
            """, firma_style),
        ]
    ]

    # Crear una tabla con las firmas
    firma_tabla = Table(firma_datos, colWidths=[250, 250])  # Ancho de columnas

    # Estilo para la tabla
    firma_tabla.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Alineación vertical
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alineación horizontal
        ('BOX', (0, 0), (-1, -1), 0, colors.white),  # Sin borde externo
        ('INNERGRID', (0, 0), (-1, -1), 0, colors.white),  # Sin líneas internas
    ]))

    # Agregar la tabla al PDF
    elements.append(firma_tabla)

    # Agregar espacio para la firma de la institución
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("""
        FIRMA DE REPRESENTANTE DE LA INSTITUCIÓN:<br/><br/>
        ____________________________<br/>
        ACLARACIÓN: Moreno, Rodolfo Jonatan<br/>
        FECHA: ____________________________
    """, firma_style))

    # Generar el PDF
    doc.build(elements)

    # Devolver el PDF como respuesta
    return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename=f"Contrato_{estudiante.cuil_estudiante}.pdf")
"""def estudiante_consultar(request):

    Vista para consultar alumnos.

    query = request.GET.get('query', '')  # Captura el término de búsqueda del formulario
    alumnos = Alumno.objects.filter(
        nombres_alumno__icontains=query
    ) | Alumno.objects.filter(
        apellidos_alumno__icontains=query
    )  # Filtra por nombre o apellido
    return render(request, 'administracion_alumnos/estudiante_consultar.html', {'alumnos': alumnos, 'query': query})

def estudiante_consultar(request):
    estudiante = None
    error = None

    if request.method == "POST":
        cuil = request.POST.get('cuil')
        if not cuil or not re.fullmatch(r'\d+', cuil):
            error = 'El CUIL debe contener solo números y no puede estar vacío.'
        else:
            try:
                estudiante = Estudiante.objects.get(cuil_estudiante=cuil)
            except Estudiante.DoesNotExist:
                error = 'No se encontró un estudiante con ese CUIL.'

    return render(request, 'administracion_alumnos/estudiante_consultar.html', {'estudiante': estudiante, 'error': error})

"""

# def estudiante_list(request):
#     estudiantes = Estudiante.objects.all()
#     return render(request, 'administracion_alumnos/estudiante_list.html',  {'estudiantes': estudiantes})
