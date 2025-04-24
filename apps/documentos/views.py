from django.shortcuts import render, redirect
from django.conf import settings
from .forms import ConsultaForm, DocumentoForm
from .google_drive import search_files_in_drive, download_file, get_drive_service
import logging
import os
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
import re
import docx
import openpyxl
from datetime import datetime
import hashlib
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from .google_drive import get_drive_service, search_files_in_drive
from django.contrib.auth.decorators import user_passes_test
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from django.conf import settings
from .google_drive import get_drive_service, search_files_in_drive, download_file, vaciar_carpeta_drive

from .google_drive import get_drive_service, descargar_archivos_desde_carpeta

# Configurar ruta al token
TOKEN_PATH = os.path.join(settings.BASE_DIR, 'token.json')

# Configura el logger
logger = logging.getLogger(__name__)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image_path):
    try:
        image = Image.open(image_path)
        # Convertir la imagen a escala de grises
        image = image.convert('L')
        # Aplicar filtros adicionales si es necesario
        image = image.point(lambda x: 0 if x < 150 else 255, '1')  # Cambiar umbral según necesidad
        return image
    except Exception as e:
        logger.error(f"Error al preprocesar la imagen {image_path}: {e}")
        return None

def extract_text_from_image(image_path):
    try:
        # Asegúrate de que las rutas sean válidas
        image = Image.open(rf'{image_path}')
        # Configuraciones de Tesseract
        config = '--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, config=config, lang='spa')
        return text
    except Exception as e:
        logger.error(f"Error al extraer texto de la imagen {image_path}: {e}")
        return ""

def extract_text_from_pdf(pdf_path):
    try:
        document = fitz.open(pdf_path)
        text = ""
        for page_num in range(document.page_count):
            page = document.load_page(page_num)
            text += page.get_text()
        return text
    except Exception as e:
        logger.error(f"Error al extraer texto del archivo PDF {pdf_path}: {e}")
        return ""

def extract_text_from_docx(docx_path):
    try:
        doc = docx.Document(docx_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        logger.error(f"Error al extraer texto del archivo DOCX {docx_path}: {e}")
        return ""

def extract_text_from_xlsx(xlsx_path):
    try:
        wb = openpyxl.load_workbook(xlsx_path, data_only=True)
        text = []
        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                text.extend([str(cell) for cell in row if cell is not None])
        return ' '.join(text)
    except Exception as e:
        logger.error(f"Error al extraer texto del archivo XLSX {xlsx_path}: {e}")
        return ""

def limpiar_texto(texto):
    """Elimina caracteres especiales y convierte el texto a minúsculas para una comparación más robusta."""
    return re.sub(r'[^A-Za-z0-9\s]', '', texto).strip().lower()

def buscar_termino(texto, consulta):
    """Realiza la búsqueda del término en el texto. Considera palabras similares o cercanas."""
    texto_limpio = limpiar_texto(texto)
    consulta_limpia = limpiar_texto(consulta)

    if consulta_limpia in texto_limpio:
        return True

    texto_palabras = texto_limpio.split()
    consulta_palabras = consulta_limpia.split()

    for palabra in consulta_palabras:
        if any(palabra in palabra_texto for palabra_texto in texto_palabras):
            return True

    return False

# Vista de consulta con búsqueda solo en modo local
def consulta_view(request):
    resultados = None
    cantidad_archivos = 0
    search_done = False

    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            search_done = True
            consulta = form.cleaned_data['consulta']
            fecha_inicio = form.cleaned_data['fecha_inicio']
            fecha_fin = form.cleaned_data['fecha_fin']
            logger.info(f"Consulta: {consulta}, Fecha desde: {fecha_inicio}, Fecha hasta: {fecha_fin}")
            resultados = []

            archivos_dir = settings.ARCHIVOS_DIR
            for root, dirs, files in os.walk(archivos_dir):
                for file_name in files:
                    try:
                        archivo_path = os.path.join(root, file_name)
                        texto = ""
                        fecha_modificacion = datetime.fromtimestamp(os.path.getmtime(archivo_path)).date()

                        # Filtro por fecha de modificación
                        if fecha_inicio and fecha_modificacion < fecha_inicio:
                            continue
                        if fecha_fin and fecha_modificacion > fecha_fin:
                            continue

                        if file_name.lower().endswith('.pdf'):
                            texto = extract_text_from_pdf(archivo_path)
                        elif file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                            texto = extract_text_from_image(archivo_path)
                        elif file_name.lower().endswith('.docx'):
                            texto = extract_text_from_docx(archivo_path)
                        elif file_name.lower().endswith('.xlsx'):
                            texto = extract_text_from_xlsx(archivo_path)

                        if buscar_termino(texto, consulta):
                            ruta_archivo = obtener_ruta_archivo(file_name)
                            if ruta_archivo:
                                resultados.append({
                                    'nombre': file_name,
                                    'url': ruta_archivo,
                                    'fecha': fecha_modificacion.strftime('%d/%m/%Y')
                                })
                    except Exception as e:
                        logger.error(f"Error procesando archivo {file_name}: {e}")

            cantidad_archivos = len(resultados)

    else:
        form = ConsultaForm()

    context = {
        'form': form,
        'resultados': resultados if resultados else None,
        'cantidad_archivos': cantidad_archivos,
        'search_done': search_done
    }
    return render(request, 'documentos/consulta.html', context)

def subir_comprobante_view(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('consulta')
    else:
        form = DocumentoForm()
    return render(request, 'documentos/subir_comprobante.html', {'form': form})

def archivo_existe(ruta_descarga, nombre_archivo):
    archivo_path = os.path.join(ruta_descarga, nombre_archivo)
    return os.path.exists(archivo_path)

# Verifica si el archivo ya existe en la ruta de descarga o en la carpeta principal de documentos.
def obtener_ruta_archivo(file_name):
    # Ruta en /media/documentos
    ruta_documentos = os.path.join(settings.MEDIA_ROOT, 'documentos', file_name)
    
    # Ruta en /media/documentos/descargados
    ruta_descargados = os.path.join(settings.MEDIA_ROOT, 'documentos', 'descargados', file_name)
    
    # Verificar si el archivo existe en alguna de las dos rutas
    if os.path.exists(ruta_documentos):
        return os.path.join(settings.MEDIA_URL, 'documentos', file_name)
    elif os.path.exists(ruta_descargados):
        return os.path.join(settings.MEDIA_URL, 'documentos', 'descargados', file_name)
    else:
        return None
    

from django.shortcuts import render, redirect
from .forms import DocumentoForm

def subir_comprobante(request):
    """
    Vista para subir comprobantes.
    """
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('consulta_comprobantes')  # Redirige a consulta_comprobantes tras subir
    else:
        form = DocumentoForm()

    return render(request, 'documentos/subir_comprobante.html', {'form': form})


# Nueva función: Descargar archivos desde Google Drive
from django.conf import settings
from django.shortcuts import render
from .google_drive import search_files_in_drive, get_drive_service, download_file
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def archivo_existe(ruta, nombre_archivo):
    """Verifica si un archivo ya existe en la ruta de destino."""
    return os.path.exists(os.path.join(ruta, nombre_archivo))

from django.shortcuts import render, redirect

def descargar_archivos_nube(request):
    try:
        # Buscar archivos en Google Drive
        drive_files = search_files_in_drive(settings.DRIVE_FOLDER_ID)
        service = get_drive_service()

        if not drive_files:
            logger.info("No se encontraron archivos en la carpeta de Google Drive.")
            return render(request, 'documentos/sin_archivos.html')

        # Ruta de descarga
        ruta_descarga = os.path.join(settings.MEDIA_ROOT, 'documentos', 'descargados')
        if not os.path.exists(ruta_descarga):
            os.makedirs(ruta_descarga)

        archivos_descargados = []
        archivos_omitidos = []

        for file in drive_files:
            try:
                file_id = file['id']
                file_name = file['name']

                # Generar el nuevo nombre basado en el ID
                extension = os.path.splitext(file_name)[1]
                nuevo_nombre = f"{file_id}{extension}"

                # Verificar si el archivo ya existe
                if archivo_existe(ruta_descarga, nuevo_nombre):
                    logger.info(f"El archivo {nuevo_nombre} ya existe. Omitiendo descarga.")
                    archivos_omitidos.append(nuevo_nombre)
                else:
                    # Descargar el archivo y guardarlo
                    archivo_path = download_file(service, file_id, nuevo_nombre, ruta_descarga)
                    if archivo_path:
                        logger.info(f"Archivo {file_name} descargado exitosamente como {nuevo_nombre}.")
                        archivos_descargados.append(nuevo_nombre)
                    else:
                        logger.error(f"No se pudo obtener el contenido del archivo {file_name}.")
            except Exception as e:
                logger.error(f"Error descargando archivo {file_name}: {e}")
                return render(request, 'documentos/error_descarga.html', {'mensaje_error': f"Error descargando archivo {file_name}: {e}"})

        # Guardar resultados en la sesión para usarlos en la página de éxito
        request.session['archivos_descargados'] = archivos_descargados
        request.session['archivos_omitidos'] = archivos_omitidos

        # Redirigir a la página de éxito
        return redirect('exito_descarga')
    except Exception as e:
        logger.error(f"Error en la descarga de archivos: {e}")
        return render(request, 'documentos/error_descarga.html', {'mensaje_error': f"Error en la descarga de archivos: {e}"})


def exito_descarga(request):
    # Recuperar los resultados de la sesión
    archivos_descargados = request.session.get('archivos_descargados', [])
    archivos_omitidos = request.session.get('archivos_omitidos', [])

    return render(request, 'documentos/exito_descarga.html', {
        'archivos_descargados': archivos_descargados,
        'archivos_omitidos': archivos_omitidos
    })

    
"""
def descargar_archivos_nube(request):
    try:
        # Buscar archivos en la carpeta de Google Drive
        drive_files = search_files_in_drive(settings.DRIVE_FOLDER_ID)
        if not drive_files:
            logger.info("No se encontraron archivos en la carpeta de Google Drive.")
            return render(request, 'documentos/sin_archivos.html')

        # Configurar la ruta de descarga
        ruta_descarga = os.path.join(settings.MEDIA_ROOT, 'documentos', 'descargados')
        if not os.path.exists(ruta_descarga):
            os.makedirs(ruta_descarga)

        archivos_descargados = []
        archivos_omitidos = []

        # Obtener el servicio autenticado de Google Drive
        service = get_drive_service()
        if not service:
            logger.error("No se pudo autenticar el servicio de Google Drive.")
            return render(request, 'documentos/error_descarga.html', {
                'mensaje_error': "No se pudo autenticar el servicio de Google Drive."
            })

        # Procesar cada archivo en la carpeta de Google Drive
        for file in drive_files:
            file_id = file['id']
            file_name = f"{file_id}"  # Usar solo el ID como nombre del archivo

            archivo_path = os.path.join(ruta_descarga, file_name)

            # Verificar si el archivo ya existe
            if os.path.exists(archivo_path):
                logger.info(f"El archivo {file_name} ya existe. Omitiendo descarga.")
                archivos_omitidos.append(file_name)
                continue

            # Descargar el archivo
            try:
                request = service.files().get_media(fileId=file_id)
                with open(archivo_path, 'wb') as archivo_local:
                    downloader = MediaIoBaseDownload(archivo_local, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                        logger.info(f"Descargando {file_name}: {int(status.progress() * 100)}%.")
                archivos_descargados.append(file_name)
                logger.info(f"Archivo {file_name} descargado correctamente.")
            except HttpError as error:
                logger.error(f"Error al descargar el archivo {file_name} (ID: {file_id}): {error}")

        # Renderizar el resumen de descargas
        return render(request, 'documentos/resumen_descarga.html', {
            'archivos_descargados': archivos_descargados,
            'archivos_omitidos': archivos_omitidos
        })

    except Exception as e:
        logger.error(f"Error en la descarga de archivos: {e}")
        return render(request, 'documentos/error_descarga.html', {
            'mensaje_error': f"Error en la descarga de archivos: {e}"
        })

"""

#NUEVO DESCARGAR ARCHIVOS  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from django.http import JsonResponse

from .google_drive import get_drive_service

DRIVE_FOLDER_ID = '1BGucPl_22qKLBcEnyQpQRR_BBTjqPEc_zzmwJzcF-hkJQR7USfZPqUrTAmhTemD8OoQqhy3Z'

def list_files(request):
    drive_service = authenticate_drive()
    query = f"'{DRIVE_FOLDER_ID}' in parents and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    return JsonResponse({'files': files})



from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import ConsultaForm
from django.shortcuts import render
from .forms import ConsultaForm
from django.shortcuts import render
from .forms import ConsultaForm

def consulta_comprobantes(request):
    """
    Vista para consultar documentos en Google Drive.
    """
    form = ConsultaForm()
    resultados = []
    cantidad_archivos = 0
    search_done = False

    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            consulta = form.cleaned_data.get('consulta')
            fecha_inicio = form.cleaned_data.get('fecha_inicio')
            fecha_fin = form.cleaned_data.get('fecha_fin')

            # Lógica de búsqueda en Google Drive
            drive_service = authenticate_drive()
            query = "trashed = false"

            # Filtrar por consulta si existe
            if consulta:
                query += f" and name contains '{consulta}'"

            # Obtener archivos de Google Drive
            results = drive_service.files().list(q=query, fields="files(id, name, modifiedTime)").execute()
            files = results.get('files', [])

            # Filtrar por fechas si están definidas
            for file in files:
                file_fecha = file.get('modifiedTime', '')[:10]  # Extraer solo la fecha
                if fecha_inicio and file_fecha < str(fecha_inicio):
                    continue
                if fecha_fin and file_fecha > str(fecha_fin):
                    continue
                resultados.append({
                    'nombre': file['name'],
                    'url': f"https://drive.google.com/file/d/{file['id']}/view",
                    'fecha': file_fecha,
                })

            cantidad_archivos = len(resultados)
            search_done = True

    return render(request, 'documentos/consulta_comprobantes.html', {
        'form': form,
        'resultados': resultados,
        'cantidad_archivos': cantidad_archivos,
        'search_done': search_done,
    })


def vaciar_carpeta_drive(request):
    """
    Vacía la carpeta de Google Drive eliminando todos los archivos.
    """
    if request.method == 'POST':
        try:
            drive_service = authenticate_drive()
            query = "trashed = false"
            results = drive_service.files().list(q=query, fields="files(id)").execute()
            files = results.get('files', [])
            deleted_files = []

            # Elimina cada archivo
            for file in files:
                drive_service.files().delete(fileId=file['id']).execute()
                deleted_files.append(file['id'])

            # Retorna una respuesta exitosa con los archivos eliminados
            return JsonResponse({'status': 'success', 'deleted_files': deleted_files})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})