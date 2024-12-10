import os
import re
from .models import Estudiante
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, FileResponse
from .forms import EstudianteForm
from django.contrib import messages
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO
from django.conf import settings
from datetime import datetime
from django.utils import timezone
from .models import EstadoDocumentacion
from django.urls import reverse


def estudiante_lista(request):
    estudiantes = Estudiante.objects.all()
    if not estudiantes:
        return HttpResponse("No se encontraron estudiantes en la base de datos.")
    return render(request, 'administracion_alumnos/estudiante_list.html', {'alumnos': alumnos})

def estudiante_list(request):
    # Obtener todos los estudiantes con sus estados de documentación
    estudiantes = Estudiante.objects.all()
    estudiantes = Estudiante.objects.all().prefetch_related('estados_documentacion')

    # Inicializar listas vacías para los estudiantes pendientes y aprobados
    estudiantes_pendientes = []
    estudiantes_aprobados = []

    # Recorrer todos los estudiantes y separarlos según su estado
    for estudiante in estudiantes:
        # Verificar si existe un estado 'pendiente' en los estados de documentación
        if estudiante.estados_documentacion.filter(estado='pendiente'):
            estudiantes_pendientes.append(estudiante)
        # Verificar si existe un estado 'aprobado' en los estados de documentación
        elif estudiante.estados_documentacion.filter(estado='aprobado'):
            estudiantes_aprobados.append(estudiante)

    # Verificar si no existen estudiantes en ninguno de los estados
    if not estudiantes_pendientes and not estudiantes_aprobados:
        return HttpResponse("No se encontraron estudiantes en la base de datos.")
    
    # Renderizar la plantilla y pasar los resultados de las consultas
    return render(request, 'administracion_alumnos/estudiante_list.html', {
        'estudiantes': estudiantes,
        'estudiantes_pendientes': estudiantes_pendientes,
        'estudiantes_aprobados': estudiantes_aprobados
    })

# def estudiante_list(request):
#     estudiantes = Estudiante.objects.all()
#     return render(request, 'administracion_alumnos/estudiante_list.html',  {'estudiantes': estudiantes})

def cambiar_estado(request, estudiante_id):
    # Obtener el registro de estado_documentacion
    estado_doc = get_object_or_404(EstadoDocumentacion, estudiante_id=estudiante_id, estado='pendiente')

    # Actualizar el estado a aprobado
    estado_doc.estado = 'aprobado'
    estado_doc.save()

    # Redirigir a una vista de éxito o listado, por ejemplo
    return redirect('estado_documentacion_list')

def estudiante_detail(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    return render(request, 'administracion_alumnos/estudiante_detail.html', {'estudiante': estudiante})

def ver_datos_estudiante(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    # Crea un diccionario dinámico con todos los campos del modelo
    campos_estudiante = {
        field.verbose_name: getattr(estudiante, field.name)
        for field in estudiante._meta.fields
    }
    return render(
        request,
        'administracion_alumnos/ver_datos_estudiante.html',
        {'estudiante': estudiante, 'campos_estudiante': campos_estudiante}
    )

def estudiante_edit(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    if request.method == "POST":
        form = EstudianteForm(request.POST, request.FILES, instance=estudiante)
        if form.is_valid():
            form.save()
            messages.success(request, 'Los cambios han sido guardados correctamente.')
            return redirect('estudiante_detail', pk=estudiante.pk)
    else:
        form = EstudianteForm(instance=estudiante)
    return render(request, 'administracion_estudiantes/estudiante_edit.html', {'form': form})


def estudiante_delete(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    if request.method == "POST":
        estudiante.delete()
        messages.success(request, 'Estudiante eliminado correctamente.')
        return redirect('estudiante_list')
    return render(request, 'administracion_estudiantes/estudiante_confirm_delete.html', {'estudiante': estudiante})



def registrar_estudiante(request):
    if request.method == 'POST':
        form = EstudianteForm(request.POST)
        if form.is_valid():
            estudiante = form.save(commit=False)
            estudiante.marca_temporal = timezone.localtime(timezone.now())  # Registrar fecha y hora actual
            estudiante.save()
            messages.success(request, 'Estudiante registrado correctamente.')
            return redirect('estudiante_list')
        else:
            messages.error(request, 'Por favor, corrija los errores a continuación.')
    else:
        form = EstudianteForm()
    return render(request, 'administracion_estudiantes/registrar_estudiante.html', {'form': form})


# Función para generar un PDF con todos los campos del estudiante
def generar_pdf_estudiante_view(request, estudiante_id):
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

def generar_pdf_estudiante(estudiante, datos_institucion, logo_path):
    
    pdf_path = f"Ficha del Estudiante - {estudiante.cuil_estudiante}.pdf"

    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d-%H%M")
    
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20,
        title="Ficha del Estudiante",  # Título del documento
        author="Hogar de Bethania",  # Autor
        subject="Ficha del estudiante - Campos informativos",  # Asunto
        creator="SEIS - || Gestión de Datos ||"  # Creador
    )


    styles = getSampleStyleSheet()
    elements = []

    # Agregar logo
    try:
        if os.path.exists(logo_path):
            logo = Image(logo_path, 1*inch, 1*inch)
            elements.append(logo)
    except FileNotFoundError:
        elements.append(Paragraph("Logo no disponible", styles['Normal']))



    # Información de la institución
    elements.append(Paragraph(datos_institucion["Nombre"], styles['Title']))
    elements.append(Paragraph(datos_institucion["Dirección"], styles['Normal']))
    elements.append(Paragraph(f"Teléfono: {datos_institucion['Teléfono']}", styles['Normal']))
    elements.append(Paragraph(f"Email: {datos_institucion['Email']}", styles['Normal']))

    # Datos del estudiante
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph("Ficha del Estudiante", styles['Heading2']))

    # Crear una lista con todos los campos del estudiante
    datos_estudiante = [
        ["Marca Temporal", estudiante.marca_temporal],
        ["Formulario Email", estudiante.email_registro],
        ["Foto", estudiante.foto_estudiante],
        ["Salita/Grado/Año", estudiante.salita_grado_anio_estudiante],
        ["Nivel", estudiante.nivel_estudiante],
        ["Número Legajo", estudiante.num_legajo_estudiante],
        ["Fecha Recepción", estudiante.fecha_recepcion],
        ["Apellidos", estudiante.apellidos_estudiante],
        ["Nombres", estudiante.nombres_estudiante],
        ["Sexo", estudiante.sexo_estudiante],
        ["Fecha Nacimiento", estudiante.fecha_nac_estudiante],
        ["Nacionalidad", estudiante.nacionalidad_estudiante],
        ["Ciudad", estudiante.ciudad_estudiante],
        ["Calle", estudiante.calle_estudiante],
        ["Número Casa", estudiante.n_mz_pc_estudiante],
        ["Barrio", estudiante.barrio_estudiante],
        ["Código Postal", estudiante.codigo_postal_estudiante],
        ["Provincia", estudiante.provincia_estudiante],
        ["CUIL", estudiante.cuil_estudiante],
        ["DNI", estudiante.dni_estudiante],
        ["Email Alumno", estudiante.email_estudiante],
        ["Religión", estudiante.religion_estudiante],
        ["Teléfono Fijo", estudiante.tel_fijo_estudiante],
        ["Teléfono Celular", estudiante.tel_cel_estudiante],
        ["Teléfono Emergencia", estudiante.tel_emergencia_estudiante],
        ["Parentesco", estudiante.parentesco_estudiante],
        ["Peso", estudiante.peso_estudiante],
        ["Talla", estudiante.talla_estudiante],
        ["Obra Social", estudiante.obra_social_estudiante],
        ["Cuál Obra Social", estudiante.cual_osocial_estudiante],
        ["Problema Neurológico", estudiante.problema_neurologico_estudiante],
        ["Cuál Problema Neurológico", estudiante.cual_prob_neurologico_estudiante],
        ["Problema Actividad Física", estudiante.problema_fisico_estudiante],
        ["Certificado Médico", estudiante.certificado_medico_estudiante],
        ["Problema Aprendizaje", estudiante.problema_aprendizaje_estudiante],
        ["Cuál Problema Aprendizaje", estudiante.cual_aprendizaje_estudiante],
        ["Atención Médica", estudiante.atencion_medica_estudiante],
        ["Alérgico", estudiante.alergia_estudiante],
        ["DNI Responsable 1", estudiante.dni_responsable1],
        ["Apellido Responsable 1", estudiante.apellidos_responsable1],
        ["Nombre Responsable 1", estudiante.nombres_responsable1],
        ["Nacionalidad Responsable 1", estudiante.nacionalidad_responsable1],
        ["Fecha Nacimiento Responsable 1", estudiante.fecha_nac_responsable1],
        ["Estado Civil Responsable 1", estudiante.estado_civil_responsable1],
        ["CUIL Responsable 1", estudiante.cuil_responsable1],
        ["Nivel Instrucción Responsable 1", estudiante.nivel_instruccion_responsable1],
        ["Calle Responsable 1", estudiante.calle_responsable1],
        ["N°/MZ/PC Responsable 1", estudiante.n_mz_pc_responsable1],
        ["Barrio Responsable 1", estudiante.barrio_responsable1],
        ["Ciudad Responsable 1", estudiante.ciudad_responsable1],
        ["Código Postal Responsable 1", estudiante.codigo_postal_responsable1],
        ["Provincia Responsable 1", estudiante.provincia_responsable1],
        ["Email Responsable 1", estudiante.email_responsable1],
        ["Religión Responsable 1", estudiante.religion_responsable1],
        ["Teléfono Fijo Responsable 1", estudiante.tel_fijo_responsable1],
        ["Teléfono Celular Responsable 1", estudiante.tel_cel_responsable1],
        ["Ocupación Responsable 1", estudiante.ocupacion_responsable1],
        ["Teléfono Laboral Responsable 1", estudiante.tel_laboral_responsable1],
        ["Horario Laboral Responsable 1", estudiante.horario_trab_responsable1],
        ["DNI Responsable 2", estudiante.dni_responsable2],
        ["Apellido Responsable 2", estudiante.apellidos_responsable2],
        ["Nombre Responsable 2", estudiante.nombres_responsable2],
        ["Nacionalidad Responsable 2", estudiante.nacionalidad_responsable2],
        ["Fecha Nacimiento Responsable 2", estudiante.fecha_nac_responsable2],
        ["Estado Civil Responsable 2", estudiante.estado_civil_responsable2],
        ["CUIL Responsable 2", estudiante.cuil_responsable2],
        ["Nivel Instrucción Responsable 2", estudiante.nivel_instruccion_responsable2],
        ["Calle Responsable 2", estudiante.calle_responsable2],
        ["N°/MZ/PC Responsable 2", estudiante.n_mz_pc_responsable2],
        ["Barrio Responsable 2", estudiante.barrio_responsable2],
        ["Ciudad Responsable 2", estudiante.ciudad_responsable2],
        ["Código Postal Responsable 2", estudiante.codigo_postal_responsable2],
        ["Provincia Responsable 2", estudiante.provincia_responsable2],
        ["Email Responsable 2", estudiante.email_responsable2],
        ["Religión Responsable 2", estudiante.religion_responsable2],
        ["Teléfono Fijo Responsable 2", estudiante.tel_fijo_responsable2],
        ["Teléfono Celular Responsable 2", estudiante.tel_cel_responsable2],
        ["Ocupación Responsable 2", estudiante.ocupacion_responsable2],
        ["Teléfono Laboral Responsable 2", estudiante.tel_laboral_responsable2],
        ["Horario Laboral Responsable 2", estudiante.horario_trab_responsable2],
        ["DNI Responsable Otro", estudiante.dni_responsable_otro],
        ["Apellido Responsable Otro", estudiante.apellidos_responsable_otro],
        ["Nombre Responsable Otro", estudiante.nombres_responsable_otro],
        ["Nacionalidad Responsable Otro", estudiante.nacionalidad_responsable_otro],
        ["Fecha Nacimiento Responsable Otro", estudiante.fecha_nac_responsable_otro],
        ["Estado Civil Responsable Otro", estudiante.estado_civil_responsable_otro],
        ["CUIL Responsable Otro", estudiante.cuil_responsable_otro],
        ["Nivel Instrucción Responsable Otro", estudiante.nivel_instruccion_responsable_otro],
        ["Calle Responsable Otro", estudiante.calle_responsable_otro],
        ["N°/MZ/PC Responsable Otro", estudiante.n_mz_pc_responsable_otro],
        ["Barrio Responsable Otro", estudiante.barrio_responsable_otro],
        ["Ciudad Responsable Otro", estudiante.ciudad_responsable_otro],
        ["Código Postal Responsable Otro", estudiante.codigo_postal_responsable_otro],
        ["Provincia Responsable Otro", estudiante.provincia_responsable_otro],
        ["Email Responsable Otro", estudiante.email_responsable_otro],
        ["Religión Responsable Otro", estudiante.religion_responsable_otro],
        ["Teléfono Fijo Responsable Otro", estudiante.tel_fijo_responsable_otro],
        ["Teléfono Celular Responsable Otro", estudiante.tel_cel_responsable_otro],
        ["Ocupación Responsable Otro", estudiante.ocupacion_responsable_otro],
        ["Teléfono Laboral Responsable Otro", estudiante.tel_laboral_responsable_otro],
        ["Horario Laboral Responsable Otro", estudiante.horario_trab_responsable_otro],
        ["Año Cursado", estudiante.anio_cursado],
        ["Dónde Cursado", estudiante.donde_cursado],
        ["Asignaturas Pendientes", estudiante.asignaturas_pendientes],
        ["Indica Asignaturas Pendientes", estudiante.indica_asig_pendientes],
        ["Tiene Hermanos en la Institución", estudiante.tiene_hermanos_institucion],
        ["Cuántos Hermanos", estudiante.cuantos_hermanos],
        ["Nivel Inicial 3", estudiante.nivel_inicial3],
        ["Nivel Inicial 4", estudiante.nivel_inicial4],
        ["Nivel Inicial 5", estudiante.nivel_inicial5],
        ["Nivel Primario 1", estudiante.nivel_primario1],
        ["Nivel Primario 2", estudiante.nivel_primario2],
        ["Nivel Primario 3", estudiante.nivel_primario3],
        ["Nivel Primario 4", estudiante.nivel_primario4],
        ["Nivel Primario 5", estudiante.nivel_primario5],
        ["Nivel Primario 6", estudiante.nivel_primario6],
        ["Nivel Primario 7", estudiante.nivel_primario7],
        ["Nivel Secundario 1", estudiante.nivel_secundario1],
        ["Nivel Secundario 2", estudiante.nivel_secundario2],
        ["Nivel Secundario 3", estudiante.nivel_secundario3],
        ["Nivel Secundario 4", estudiante.nivel_secundario4],
        ["Nivel Secundario 5", estudiante.nivel_secundario5],
        ["Cómo Conociste la Institución", estudiante.como_conociste_institucion],
        ["Eligió la Institución", estudiante.eligio_institucion],
        ["Nivel de Enseñanza", estudiante.nivel_ensenanza],
        ["Ciudad a los Días", estudiante.ciudad_a_los_dias],
        ["Señores 1", estudiante.senores1],
        ["DNI Señores 1", estudiante.dni_senores1],
        ["Señores 2", estudiante.senores2],
        ["DNI Señores 2", estudiante.dni_senores2],
        ["Domicilios Señores", estudiante.domicilios_senores],
        ["Domicilio Especial Electrónico", estudiante.domicilio_especial_electronico],
        ["Actúan Nombres Estudiante", estudiante.actuan_nombres_estudiante],
        ["DNI Actúan Estudiante", estudiante.dni_acutan_estudiante],
        ["Domicilio Actúan Estudiante", estudiante.domicilio_actuan_estudiante],
        ["Responsable de Pago", estudiante.responsable_pago],
        ["DNI Responsable de Pago", estudiante.dni_responsable_pago],
        ["Manifiesta Responsable", estudiante.manifiesta_responsable],
        ["Autoriza Facturación", estudiante.autoriza_facturacion],
        ["Autoriza Imagen", estudiante.autoriza_imagen]
    ]
    # Filtrar campos completos
    datos_estudiante = [[label, value] for label, value in datos_estudiante if value]

    # Crear una tabla con los datos filtrados
    tabla = Table(datos_estudiante, colWidths=[3*inch, 3.5*inch])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))
    elements.append(tabla)

    # Generar el PDF
    doc.build(elements)
    return pdf_path

def generar_pdf_lista_estudiantes_view(request):
    # Configuración del PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="lista_estudiantes.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=15, bottomMargin=30)

    styles = getSampleStyleSheet()
    elements = []

    # Agregar el logo de la institución
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    try:
        if os.path.exists(logo_path):
            logo = Image(logo_path, 1 * inch, 1 * inch)
            elements.append(logo)
    except FileNotFoundError:
        elements.append(Paragraph("Logo no disponible", styles['Normal']))

    # Título del PDF
    elements.append(Paragraph("Lista de Estudiantes", styles['Title']))

    # Obtener los datos de los estudiantes
    estudiantes = Estudiante.objects.all().order_by('nivel_estudiante', 'apellidos_estudiante')

    # Encabezados de la tabla
    data = [["CUIL", "Apellido/s", "Nombre/s", "Nivel", "Teléfono"]]

    # Filas de datos
    for estudiante in estudiantes:
        data.append([
            estudiante.cuil_estudiante,
            estudiante.apellidos_estudiante,
            estudiante.nombres_estudiante,
            estudiante.nivel_estudiante,
            estudiante.tel_cel_estudiante
        ])

    # Configuración de la tabla
    tabla = Table(data, colWidths=[1.5 * inch, 1.5 * inch, 1.5 * inch, 1 * inch, 1.5 * inch])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Color de encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Color del texto del encabezado
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Alineación de texto
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fuente del encabezado
        ('FONTSIZE', (0, 0), (-1, -1), 9),  # Tamaño de la fuente
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Líneas de la tabla
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Fondo de las celdas
    ]))
    elements.append(tabla)

    # Generar el PDF
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
        leftMargin=10,
        topMargin=10,
        bottomMargin=20,
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
    elements.append(Spacer(1, 0.5 * inch))
    # Usar el estilo personalizado Título del contrato
    elements.append(Paragraph("CONTRATO DE ENSEÑANZA EDUCATIVA CICLO LECTIVO 2025", custom_title_style))

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
