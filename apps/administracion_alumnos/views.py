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
    if request.method == "POST":
        cuil = request.POST.get('cuil')
        try:
            alumno = Alumno.objects.get(cuil_alumno=cuil)
        except Alumno.DoesNotExist:
            return render(request, 'administracion_alumnos/consultar_alumno.html', {'error': 'No se encontró un alumno con ese CUIL'})
    return render(request, 'administracion_alumnos/consultar_alumno.html', {'alumno': alumno})

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