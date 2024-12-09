import re
from .models import Estudiante
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, FileResponse
from .models import Estudiante
from .forms import EstudianteForm
from django.contrib import messages
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO
from django.conf import settings
import os
from datetime import datetime
from django.utils import timezone
from .models import EstadoDocumentacion  # Agrega esta línea si no está

def estudiante_lista(request):
    estudiantes = Estudiante.objects.all().prefetch_related('estados_documentacion')
    if not estudiantes:
        return HttpResponse("No se encontraron estudiantes en la base de datos.")
    return render(request, 'administracion_alumnos/estudiante_list.html', {'alumnos': alumnos})

def estudiante_list(request):
    # Obtener todos los estudiantes con sus estados de documentación
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
        'estudiantes_pendientes': estudiantes_pendientes,
        'estudiantes_aprobados': estudiantes_aprobados
    })

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
        "Dirección": "Urquiza Nº 846, Pcia. Roque Sáenz Peña - Chaco",
        "Teléfono": "1122334455",
        "Email": "contacto@institucion.edu"
    }
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    pdf_path = generar_pdf_estudiante(estudiante, datos_institucion, logo_path)
    return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename='ficha_estudiante.pdf')


def generar_pdf_estudiante(estudiante, datos_institucion, logo_path):
    pdf_path = "Ficha del Estudiante.pdf"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d-%H%M")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)

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
        ["Formulario Email", estudiante.formulario_email],
        ["Foto", estudiante.foto],
        ["Salita/Grado/Año", estudiante.salita_grado_ano],
        ["Nivel", estudiante.nivel],
        ["Número Legajo", estudiante.numero_legajo],
        ["Fecha Recepción", estudiante.fecha_recepcion],
        ["Apellidos", estudiante.apellidos],
        ["Nombres", estudiante.nombres],
        ["Sexo", estudiante.sexo],
        ["Fecha Nacimiento", estudiante.fecha_nacimiento],
        ["Nacionalidad", estudiante.nacionalidad],
        ["Ciudad", estudiante.ciudad],
        ["Calle", estudiante.calle],
        ["Número Casa", estudiante.numero_casa],
        ["Barrio", estudiante.barrio],
        ["Código Postal", estudiante.codigo_postal],
        ["Provincia", estudiante.provincia],
        ["CUIL", estudiante.cuil],
        ["DNI", estudiante.dni],
        ["Email Alumno", estudiante.email_alumno],
        ["Religión", estudiante.religion],
        ["Teléfono Fijo", estudiante.telefono_fijo],
        ["Teléfono Celular", estudiante.telefono_celular],
        ["Teléfono Emergencia", estudiante.telefono_emergencia],
        ["Parentesco", estudiante.parentesco],
        ["Peso", estudiante.peso],
        ["Talla", estudiante.talla],
        ["Obra Social", estudiante.obra_social],
        ["Cuál Obra Social", estudiante.cual_obra_social],
        ["Problema Neurológico", estudiante.problema_neurologico],
        ["Cuál Problema Neurológico", estudiante.cual_problema_neurologico],
        ["Problema Actividad Física", estudiante.problema_actividad_fisica],
        ["Certificado Médico", estudiante.certificado_medico],
        ["Problema Aprendizaje", estudiante.problema_aprendizaje],
        ["Cuál Problema Aprendizaje", estudiante.cual_problema_aprendizaje],
        ["Atención Médica", estudiante.atencion_medica],
        ["Alérgico", estudiante.alergico],
        ["DNI Responsable 1", estudiante.dni_responsable1],
        ["Apellido Responsable 1", estudiante.apellido_responsable1],
        ["Nombre Responsable 1", estudiante.nombre_responsable1],
        ["Nacionalidad Responsable 1", estudiante.nacionalidad_responsable1],
        ["Fecha Nacimiento Responsable 1", estudiante.fecha_nacimiento_responsable1],
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
        ["Teléfono Fijo Responsable 1", estudiante.telefono_fijo_responsable1],
        ["Teléfono Celular Responsable 1", estudiante.telefono_celular_responsable1],
        ["Ocupación Responsable 1", estudiante.ocupacion_responsable1],
        ["Teléfono Laboral Responsable 1", estudiante.telefono_laboral_responsable1],
        ["Horario Laboral Responsable 1", estudiante.horario_laboral_responsable1],
        ["DNI Responsable 2", estudiante.dni_responsable2],
        ["Apellido Responsable 2", estudiante.apellido_responsable2],
        ["Nombre Responsable 2", estudiante.nombre_responsable2],
        ["Nacionalidad Responsable 2", estudiante.nacionalidad_responsable2],
        ["Fecha Nacimiento Responsable 2", estudiante.fecha_nacimiento_responsable2],
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
        ["Teléfono Fijo Responsable 2", estudiante.telefono_fijo_responsable2],
        ["Teléfono Celular Responsable 2", estudiante.telefono_celular_responsable2],
        ["Ocupación Responsable 2", estudiante.ocupacion_responsable2],
        ["Teléfono Laboral Responsable 2", estudiante.telefono_laboral_responsable2],
        ["Horario Laboral Responsable 2", estudiante.horario_laboral_responsable2],
        ["DNI Responsable Otro", estudiante.dni_responsableOtro],
        ["Apellido Responsable Otro", estudiante.apellido_responsableOtro],
        ["Nombre Responsable Otro", estudiante.nombre_responsableOtro],
        ["Nacionalidad Responsable Otro", estudiante.nacionalidad_responsableOtro],
        ["Fecha Nacimiento Responsable Otro", estudiante.fechaNacimiento_responsableOtro],
        ["Estado Civil Responsable Otro", estudiante.estadoCivil_responsableOtro],
        ["CUIL Responsable Otro", estudiante.cuil_responsableOtro],
        ["Nivel Instrucción Responsable Otro", estudiante.NivelInstruccion_responsableOtro],
        ["Calle Responsable Otro", estudiante.calle_responsableOtro],
        ["N°/MZ/PC Responsable Otro", estudiante.n_mz_pc_responsableOtro],
        ["Barrio Responsable Otro", estudiante.barrio_responsableOtro],
        ["Ciudad Responsable Otro", estudiante.ciudad_responsableOtro],
        ["Código Postal Responsable Otro", estudiante.codigoPostal_responsableOtro],
        ["Provincia Responsable Otro", estudiante.provincia_responsableOtro],
        ["Email Responsable Otro", estudiante.email_responsableOtro],
        ["Religión Responsable Otro", estudiante.religion_responsableOtro],
        ["Teléfono Fijo Responsable Otro", estudiante.telefonoFijo_responsableOtro],
        ["Teléfono Celular Responsable Otro", estudiante.telefonoCelular_responsableOtro],
        ["Ocupación Responsable Otro", estudiante.ocupacion_responsableOtro],
        ["Teléfono Laboral Responsable Otro", estudiante.telefonoLaboral_responsableOtro],
        ["Horario Laboral Responsable Otro", estudiante.horarioLaboral_ResponsableOtro],
        ["Nivel Enseñanza", estudiante.nivel_ensenanza],
        ["Contrato Fecha", estudiante.contrato_fecha],
        ["Contrato Señores 1", estudiante.contrato_senores1],
        ["Contrato DNI Señores 1", estudiante.contrato_dniSenores1],
        ["Contrato Señores 2", estudiante.contrato_senores2],
        ["Contrato DNI Señores 2", estudiante.contrato_dniSenores2],
        ["Contrato Domicilio Señores", estudiante.contrato_domicilioSenores],
        ["Contrato Email Señores", estudiante.contrato_emailSenores],
        ["Contrato Representación Alumno", estudiante.contrato_representacionAlumno],
        ["Contrato DNI Alumno", estudiante.contrato_dniAlumno],
        ["Contrato Domicilio Alumno", estudiante.contrato_domicilioAlumno],
        ["Contrato Responsable", estudiante.contrato_responsable],
        ["Contrato DNI Responsable", estudiante.contrato_dniResponsable],
        ["Contrato Cumplimiento", estudiante.contrato_cumplimiento],
        ["Contrato Autorización Facturación", estudiante.contrato_autorizacionFacturacion],
        ["Imagen Autorizado", estudiante.imagen_autorizado],
    ]

    # Crear una tabla con los datos
    tabla = Table(datos_estudiante, colWidths=[3*inch, 3.5*inch])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Color texto encabezado
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Alineación
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fuente del encabezado
        ('FONTSIZE', (0, 0), (-1, -1), 9),  # Tamaño de fuente
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Líneas de la tabla
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Fondo de celdas
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

from django.shortcuts import render
from .models import Estudiante  # Importar el modelo Estudiante

# def estudiante_list(request):
#     estudiantes = Estudiante.objects.all()
#     return render(request, 'administracion_alumnos/estudiante_list.html',  {'estudiantes': estudiantes})


from django.shortcuts import render, get_object_or_404
from .models import Estudiante  # Asegúrate de importar el modelo correcto

from django.shortcuts import render, get_object_or_404, redirect
from .models import Estudiante  # Asegúrate de importar el modelo correcto
from .forms import EstudianteForm  # Asegúrate de tener un formulario definido

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

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Estudiante  # Asegúrate de usar el modelo correcto

def estudiante_delete(request, pk):
    """
    Vista para eliminar un alumno.
    """
    alumno = get_object_or_404(Estudiante, pk=pk)
    if request.method == "POST":
        alumno.delete()
        return redirect(reverse('estudiante_list'))  # Redirige a la lista de alumnos
    return render(request, 'administracion_alumnos/alumno_confirm_delete.html', {'alumno': alumno})


from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Estudiante  # Asegúrate de usar el modelo correcto

def estudiante_delete(request, pk):
    """
    Vista para eliminar un alumno.
    """
    alumno = get_object_or_404(Estudiante, pk=pk)
    if request.method == "POST":
        alumno.delete()
        return redirect(reverse('estudiante_list'))  # Redirige a la lista de alumnos
    return render(request, 'administracion_alumnos/alumno_confirm_delete.html', {'alumno': alumno})


"""def estudiante_consultar(request):

    Vista para consultar alumnos.

    query = request.GET.get('query', '')  # Captura el término de búsqueda del formulario
    alumnos = Alumno.objects.filter(
        nombres_alumno__icontains=query
    ) | Alumno.objects.filter(
        apellidos_alumno__icontains=query
    )  # Filtra por nombre o apellido
    return render(request, 'administracion_alumnos/estudiante_consultar.html', {'alumnos': alumnos, 'query': query})
"""
"""def estudiante_consultar(request):
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