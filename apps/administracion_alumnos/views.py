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

from .utils import search_files_in_drive, download_file, archivo_existe


from googleapiclient.http import MediaIoBaseDownload

from django.shortcuts import render
from apps.administracion_alumnos.models import Estudiante

def estudiante_lista(request):
    # Trae todos los estudiantes con sus relaciones
    estudiantes = Estudiante.objects.select_related(
        'inscripcion', 'estado_documentacion'
    ).all()

    # Filtra por estado (pendiente / aprobado)
    estudiantes_pendientes = estudiantes.filter(
        estado_documentacion__estado='Pendiente'
    )
    estudiantes_aprobados = estudiantes.filter(
        estado_documentacion__estado='Aprobado'
    )

    # Renderiza la plantilla con los datos
    return render(request, 'administracion_alumnos/estudiante_list.html', {
        'estudiantes': estudiantes,
        'estudiantes_pendientes': estudiantes_pendientes,
        'estudiantes_aprobados': estudiantes_aprobados,
    })


def confirmar_aprobacion(request, estudiante_id):
    try:
        # Buscar el registro con estado pendiente
        estado_doc = EstadoDocumentacion.objects.get(estudiante_id=estudiante_id, estado='pendiente')
    except EstadoDocumentacion.DoesNotExist:
        # Manejar el caso donde no hay un estado pendiente
        mensaje_error = "El estudiante ya está aprobado o no tiene un estado pendiente."
        return render(request, 'administracion_alumnos/error_aprobacion.html', {'mensaje_error': mensaje_error})

    # Obtener los datos del estudiante
    estudiante = estado_doc.estudiante

    if request.method == 'POST':
        # Cambiar el estado a 'aprobado' si se confirma
        estado_doc.estado = 'aprobado'
        estado_doc.save()
        return redirect('estudiante_list')  # Cambia según el flujo de tu aplicación

    # Renderizar el template de confirmación
    return render(request, 'administracion_alumnos/confirmar_aprobacion.html', {
        'estado_doc': estado_doc,
        'estudiante': estudiante,
    })

def estudiante_detail(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    return render(request, 'administracion_alumnos/estudiante_detail.html', {'estudiante': estudiante})

import os
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import Estudiante

def ver_datos_estudiante(request, pk):
    """
    Muestra los datos de un estudiante, incluyendo su foto si está disponible.
    """
    # Ruta base donde se almacenan las fotos localmente
    fotos_path = os.path.join(settings.MEDIA_ROOT, 'documentos', 'fotoPerfilEstudiante')

    # Obtener el estudiante según su ID (pk)
    estudiante = get_object_or_404(Estudiante, pk=pk)

    # Buscar la foto del estudiante basada en el CUIL o ID de Google Drive
    foto_id = None
    if estudiante.foto_estudiante:
        # Extrae el ID del enlace de Google Drive si está en el campo
        if "id=" in estudiante.foto_estudiante:
            foto_id = estudiante.foto_estudiante.split("id=")[-1]

    # Inicializar la URL de la foto
    foto_url = None
    if foto_id:
        # Verifica si existe algún archivo con el ID en su nombre en la carpeta local
        for archivo in os.listdir(fotos_path):
            if archivo.startswith(foto_id):  # Busca archivos que comiencen con el ID
                # Genera la URL para acceder a la foto desde el navegador
                foto_url = os.path.join(
                    settings.MEDIA_URL, 'documentos', 'fotoPerfilEstudiante', archivo
                )
                break

    # Si no se encuentra la foto, usar una imagen por defecto
    if not foto_url:
        foto_url = os.path.join(settings.STATIC_URL, 'images/default.jpg')

    # Renderizar la vista con los datos del estudiante y su foto
    return render(request, 'administracion_alumnos/ver_datos_estudiante.html', {
        'estudiante': estudiante,
        'image_url': foto_url  # URL de la foto del estudiante
    })


# def estudiante_edit(request, pk):
#     estudiante = get_object_or_404(Estudiante, pk=pk)
#     if request.method == "POST":
#         form = EstudianteForm(request.POST, request.FILES, instance=estudiante)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Los cambios han sido guardados correctamente.')
#             return redirect('estudiante_detail', pk=estudiante.pk)
#     else:
#         form = EstudianteForm(instance=estudiante)
#     return render(request, 'administracion_estudiantes/estudiante_edit.html', {'form': form})


# def estudiante_delete(request, pk):
#     estudiante = get_object_or_404(Estudiante, pk=pk)
#     if request.method == "POST":
#         estudiante.delete()
#         messages.success(request, 'Estudiante eliminado correctamente.')
#         return redirect('estudiante_list')
#     return render(request, 'administracion_alumnos/alumno_confirm_delete.html', {'estudiante': estudiante}) 

"""def registrar_estudiante(request):
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
    return render(request, 'administracion_alumnos/registrar_estudiante.html', {'form': form})

"""


from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import EstudianteForm

def registrar_estudiante(request):
    if request.method == 'POST':
        form = EstudianteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Estudiante registrado correctamente.")
            return redirect('registrar_alumno')  # O a donde quieras redirigir
        else:
            messages.error(request, "Por favor corregí los errores del formulario.")
    else:
        form = EstudianteForm()
    return render(request, 'administracion_alumnos/registrar_estudiante.html', {'form': form})

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


    from reportlab.lib.units import cm
    from PIL import Image as PilImage

    # Crear estilos
    styles = getSampleStyleSheet()

    # Definir tamaño objetivo en píxeles (4x4 cm ≈ 113x113 px a 72 dpi)
    target_cm = 4
    target_px = int(target_cm * cm / 0.352777778)  # 1 cm ≈ 28.35 pt; 1 pt = 0.352777778 mm

    foto_est = None
    foto_id = None
    extensiones_validas = ['.jpg', '.jpeg', '.png']

    if estudiante.foto_estudiante and "id=" in estudiante.foto_estudiante:
        foto_id = estudiante.foto_estudiante.split("id=")[-1]

    if foto_id:
        carpeta_fotos = os.path.join(settings.MEDIA_ROOT, 'documentos', 'fotoPerfilEstudiante')
        for archivo in os.listdir(carpeta_fotos):
            nombre, extension = os.path.splitext(archivo)
            if archivo.startswith(foto_id) and extension.lower() in extensiones_validas:
                ruta_foto = os.path.join(carpeta_fotos, archivo)
                if os.path.exists(ruta_foto):
                    try:
                        # Abrir imagen original
                        with PilImage.open(ruta_foto) as im:
                            width, height = im.size
                            aspect = width / height
                            target_aspect = 1  # 4x4 cm => cuadrado

                            # Recortar proporcionalmente al centro
                            if aspect > target_aspect:
                                # Imagen más ancha que alta: recortar bordes laterales
                                new_width = int(height * target_aspect)
                                left = (width - new_width) // 2
                                right = left + new_width
                                top = 0
                                bottom = height
                            else:
                                # Imagen más alta que ancha: recortar partes superior/inferior
                                new_height = int(width / target_aspect)
                                top = (height - new_height) // 2
                                bottom = top + new_height
                                left = 0
                                right = width

                            im_cropped = im.crop((left, top, right, bottom))
                            im_cropped = im_cropped.resize((int(4*cm), int(4*cm)))

                            # Guardar imagen temporal
                            temp_path = os.path.join(settings.MEDIA_ROOT, f"temp_foto_{estudiante.pk}.png")
                            im_cropped.save(temp_path)

                            # Usar en ReportLab
                            foto_est = Image(temp_path, width=4*cm, height=4*cm)

                    except Exception as e:
                        print("Error procesando imagen:", e)
                        foto_est = Paragraph("Foto no disponible", styles["Normal"])
                break

    if not foto_est:
        foto_est = Paragraph("Foto no disponible", styles["Normal"])

    # Tabla de encabezado con foto y datos de institución
    info_institucion = [
        Paragraph(datos_institucion["Nombre"], styles['Heading3']),
        Paragraph(datos_institucion["Dirección"], styles['Normal']),
        Paragraph(f"Teléfono: {datos_institucion['Teléfono']}", styles['Normal']),
        Paragraph(f"Email: {datos_institucion['Email']}", styles['Normal'])
    ]

    encabezado_tabla = Table([[info_institucion, foto_est]], colWidths=[12 * cm, 4 * cm])
    encabezado_tabla.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER')
    ]))

    elements.append(encabezado_tabla)
    elements.append(Spacer(1, 0.25 * inch))


    # Otra forma de titulo institucion 
    # Información de la institución
    #elements.append(Paragraph(datos_institucion["Nombre"], styles['Title']))
    #elements.append(Paragraph(datos_institucion["Dirección"], styles['Normal']))
    #elements.append(Paragraph(f"Teléfono: {datos_institucion['Teléfono']}", styles['Normal']))
    #elements.append(Paragraph(f"Email: {datos_institucion['Email']}", styles['Normal']))

    # Datos del estudiante
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
    tabla = Table(datos_estudiante, colWidths=[4.1*inch, 3.5*inch])
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
    alumno = get_object_or_404(Estudiante, pk=pk)
    if request.method == "POST":
        form = EstudianteForm(request.POST, instance=alumno)
        if form.is_valid():
            form.save()
            return redirect('estudiante_list')
        else:
            print(form.errors)  # Esto te dará detalles de cualquier error en el formulario
    else:
        form = EstudianteForm(instance=alumno)
    return render(request, 'administracion_alumnos/estudiante_edit.html', {'form': form})

# def estudiante_delete(request, pk):
#     """
#     Vista para eliminar un alumno.
#     """
#     alumno = get_object_or_404(Estudiante, pk=pk)
#     if request.method == "POST":
#         alumno.delete()
#         return redirect(reverse('estudiante_list'))  # Redirige a la lista de alumnos
#     return render(request, 'administracion_alumnos/alumno_confirm_delete.html', {'alumno': alumno})


def estudiante_delete(request, pk):
    # Aquí deberías usar `estudiante`, no `alumno`
    estudiante = get_object_or_404(Estudiante, pk=pk)
    
    if request.method == 'POST':
        estudiante.delete()  # Asegúrate de usar `estudiante`, no `alumno`
        return redirect('estudiante_list')
    
    return render(request, 'administracion_alumnos/alumno_confirm_delete.html', {'estudiante': estudiante})

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


from django.shortcuts import render
from django.conf import settings
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import os
import logging
from datetime import datetime
from .utils import search_files_in_drive, download_file, archivo_existe

logger = logging.getLogger(__name__)

def get_drive_service():
    """
    Crea y devuelve un cliente de Google Drive API usando las credenciales de la aplicación.
    """
    credentials_path = settings.GOOGLE_CREDENTIALS_ALUMNOS  # Configuración específica para administracion_alumnos
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"No se encontró el archivo de credenciales en: {credentials_path}")

    credentials = Credentials.from_service_account_file(
        credentials_path, scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=credentials)


def descargar_archivos_alumnos(request):
    """
    Descarga archivos desde la carpeta de Google Drive asociada a la aplicación administracion_alumnos.
    """
    try:
        drive_folder_id = settings.DRIVE_FOLDER_ID_ALUMNOS  # ID de la carpeta específica
        service = get_drive_service()

        # Buscar archivos en la carpeta de Google Drive
        drive_files = search_files_in_drive(drive_folder_id, service)

        if not drive_files:
            logger.info("No se encontraron archivos en la carpeta de Google Drive.")
            return render(request, 'administracion_alumnos/sin_archivos.html')

        # Ruta para guardar los archivos descargados
        ruta_descarga = os.path.join(settings.MEDIA_ROOT, 'administracion_alumnos', 'descargados')
        if not os.path.exists(ruta_descarga):
            os.makedirs(ruta_descarga)

        archivos_descargados = []
        archivos_omitidos = []

        # Procesar cada archivo en la carpeta de Google Drive
        for file in drive_files:
            try:
                file_id = file['id']
                file_name = file['name']
                file_data = download_file(service, file_id)

                if file_data:
                    created_time = file.get('createdTime', '')

                    # Formatear fecha de creación
                    if created_time:
                        try:
                            fecha_formateada = datetime.strptime(
                                created_time, "%Y-%m-%dT%H:%M:%S.%fZ"
                            ).strftime("%Y%m%d_%H%M%S")
                        except ValueError:
                            logger.error(f"Error al formatear la fecha {created_time}. Usando 'Fecha_desconocida'.")
                            fecha_formateada = "Fecha_desconocida"
                    else:
                        logger.warning(f"El archivo {file_name} no tiene 'createdTime'. Usando 'Fecha_desconocida'.")
                        fecha_formateada = "Fecha_desconocida"

                    # Generar un nuevo nombre único para el archivo
                    extension = os.path.splitext(file_name)[1]
                    id_corto = file_id[:8]
                    nuevo_nombre = f"alumno-{fecha_formateada}-{id_corto}{extension}"

                    # Verificar si el archivo ya existe
                    if archivo_existe(ruta_descarga, nuevo_nombre):
                        logger.info(f"El archivo {nuevo_nombre} ya existe. Omitiendo descarga.")
                        archivos_omitidos.append(nuevo_nombre)
                    else:
                        archivo_path = os.path.join(ruta_descarga, nuevo_nombre)
                        with open(archivo_path, 'wb') as archivo_local:
                            archivo_local.write(file_data)
                        logger.info(f"Archivo {file_name} descargado exitosamente como {nuevo_nombre}.")
                        archivos_descargados.append(nuevo_nombre)

                else:
                    logger.error(f"No se pudo obtener el contenido del archivo {file_name}.")
            except Exception as e:
                logger.error(f"Error descargando archivo {file_name}: {e}")
                return render(request, 'administracion_alumnos/error_descarga.html', {
                    'mensaje_error': f"Error descargando archivo {file_name}: {e}"
                })

        # Renderizar el resumen de la descarga
        return render(request, 'administracion_alumnos/resumen_descarga.html', {
            'archivos_descargados': archivos_descargados,
            'archivos_omitidos': archivos_omitidos
        })

    except Exception as e:
        logger.error(f"Error en la descarga de archivos: {e}")
        return render(request, 'administracion_alumnos/error_descarga.html', {
            'mensaje_error': f"Error en la descarga de archivos: {e}"
        })



def descargar_todos_archivos(request):
    """
    Descarga todos los archivos desde la carpeta de Google Drive asociada,
    guardándolos con su ID como nombre.
    """
    try:
        # Autenticación y servicio de Google Drive
        service = get_drive_service()
        folder_id = settings.DRIVE_FOLDER_ID_ALUMNOS  # ID de la carpeta específica

        # Consultar archivos en la carpeta de Google Drive
        query = f"'{folder_id}' in parents and trashed=false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        drive_files = results.get('files', [])

        if not drive_files:
            logger.info("No se encontraron archivos en la carpeta de Google Drive.")
            return render(request, 'administracion_alumnos/sin_archivos.html')

        # Crear carpeta local para guardar los archivos
        ruta_descarga = settings.FOTO_PERFIL_ESTUDIANTE_DIR
        os.makedirs(ruta_descarga, exist_ok=True)

        archivos_descargados = []
        for file in drive_files:
            file_id = file['id']
            file_name = file['name']
            try:
                # Descargar archivo
                request_media = service.files().get_media(fileId=file_id)

                # Cambiar el nombre del archivo al ID del archivo
                extension = os.path.splitext(file_name)[1]  # Obtener la extensión original
                nuevo_nombre = f"{file_id}{extension}"  # Nuevo nombre con ID y extensión
                archivo_path = os.path.join(ruta_descarga, nuevo_nombre)

                # Guardar el archivo localmente
                with open(archivo_path, 'wb') as archivo_local:
                    downloader = MediaIoBaseDownload(archivo_local, request_media)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                        logger.info(f"Descarga {int(status.progress() * 100)}% completada para {nuevo_nombre}.")

                archivos_descargados.append(nuevo_nombre)
            except Exception as e:
                logger.error(f"Error descargando {file_name}: {e}")

        # Renderizar el resumen de descarga
        return render(request, 'administracion_alumnos/resumen_descarga.html', {
            'archivos_descargados': archivos_descargados,
        })

    except Exception as e:
        logger.error(f"Error en la descarga de archivos: {e}")
        return render(request, 'administracion_alumnos/error_descarga.html', {
            'mensaje_error': f"Error en la descarga de archivos: {e}"
        })

from django.shortcuts import render
from .models import Estudiante
import os
from django.conf import settings

from django.shortcuts import render
from .models import Estudiante
import os
from django.conf import settings

def lista_fotos_estudiantes(request):
    """
    Genera una lista de estudiantes con sus fotos correspondientes.
    """
    # Ruta base donde se almacenan las fotos localmente
    fotos_path = settings.FOTO_PERFIL_ESTUDIANTE_DIR  # Cambiar para usar la ruta correcta

    # Lista para almacenar los datos que enviaremos al template
    fotos_estudiantes = []

    # Obtén todos los estudiantes de la base de datos
    estudiantes = Estudiante.objects.all()

    for estudiante in estudiantes:
        # Extraer el ID de la foto desde el enlace almacenado en foto_estudiante
        foto_id = None
        if estudiante.foto_estudiante:
            # Extrae el ID del enlace de Google Drive
            if "id=" in estudiante.foto_estudiante:
                foto_id = estudiante.foto_estudiante.split("id=")[-1]

        # Buscar el archivo con el ID, sin importar la extensión
        foto_url = None
        if foto_id:
            # Verifica si existe algún archivo con el ID en su nombre en la carpeta local
            for archivo in os.listdir(fotos_path):
                if archivo.startswith(foto_id):  # Busca archivos que comiencen con el ID
                    # Genera la URL para acceder a la foto desde el navegador
                    foto_url = os.path.join(
                        settings.MEDIA_URL, 'documentos', 'fotoPerfilEstudiante', archivo
                    )
                    break  # Deja de buscar después de encontrar el archivo

        # Agregar los datos del estudiante y su foto al listado
        fotos_estudiantes.append({
            "cuil": estudiante.cuil_estudiante,  # Asegúrate de que este sea el campo correcto
            "foto_url": foto_url,  # Foto del estudiante (si existe)
        })

    return render(request, 'administracion_alumnos/lista_fotos_estudiantes.html', {
        'fotos_estudiantes': fotos_estudiantes
    })

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
