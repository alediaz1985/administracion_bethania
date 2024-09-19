from django.shortcuts import render, redirect
from django.conf import settings
from .forms import ConsultaForm, DocumentoForm
from .google_drive import search_files_in_drive, download_file, extract_text_from_file, get_drive_service  # Importar funciones de Google Drive
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

# Configurar ruta al token
TOKEN_PATH = os.path.join(settings.BASE_DIR, 'token.json')

def get_drive_service():
    """Obtiene el servicio autenticado de Google Drive usando el token"""
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, scopes=['https://www.googleapis.com/auth/drive'])
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("No se pudo autenticar con el token de Google Drive.")

    # Construir el servicio
    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except HttpError as error:
        logger.error(f"Error al construir el servicio de Google Drive: {error}")
        return None

# Configura el logging
logging.basicConfig(level=logging.INFO)
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
        config = '--oem 3 --psm 6'  # Puedes ajustar estos valores según la imagen
        text = pytesseract.image_to_string(image, config=config, lang='spa')  # Especifica el idioma
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

    # Compara si la consulta está dentro del texto limpiado
    if consulta_limpia in texto_limpio:
        return True
    
    # Intenta dividir el texto y comparar las palabras
    texto_palabras = texto_limpio.split()
    consulta_palabras = consulta_limpia.split()
    
    # Compara por palabras individuales
    for palabra in consulta_palabras:
        if any(palabra in palabra_texto for palabra_texto in texto_palabras):
            return True
    
    return False

def consulta_view(request):
    resultados = None
    cantidad_archivos = 0
    search_done = False

    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            search_done = True
            consulta = form.cleaned_data['consulta']
            origen = form.cleaned_data.get('origen', 'local')  # Si no se selecciona origen, usa 'local' como predeterminado
            logger.info(f"Consulta: {consulta}, Origen: {origen}")
            resultados = []

            # Si el origen es Google Drive
            if origen == 'drive':
                # Obtener el servicio autenticado de Google Drive
                service = get_drive_service()
                if service:
                    drive_files = search_files_in_drive(service)
                    if not drive_files:
                        logger.info("No se encontraron archivos en la carpeta de Google Drive.")
                    else:
                        for file in drive_files:
                            try:
                                file_id = file['id']
                                file_name = file['name']
                                mime_type = file['mimeType']
                                created_time = file['createdTime']
                                created_time_formatted = datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d/%m/%Y')
                                web_view_link = file.get('webViewLink', '#')
                                file_data = download_file(service, file_id)
                                if file_data:
                                    texto = extract_text_from_file(file_data, mime_type)
                                    if buscar_termino(texto, consulta):
                                        resultados.append({
                                            'nombre': file_name,
                                            'url': web_view_link,
                                            'fecha': created_time_formatted
                                        })
                            except Exception as e:
                                logger.error(f"Error procesando archivo {file_name}: {e}")

            # Por defecto o si el origen es local
            elif origen == 'local':
                archivos_dir = settings.ARCHIVOS_DIR
                for root, dirs, files in os.walk(archivos_dir):
                    for file_name in files:
                        try:
                            archivo_path = os.path.join(root, file_name)
                            mime_type = None
                            texto = ""

                            if file_name.lower().endswith('.pdf'):
                                mime_type = 'application/pdf'
                                texto = extract_text_from_pdf(archivo_path)
                            elif file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                                mime_type = 'image/jpeg'
                                texto = extract_text_from_image(archivo_path)
                            elif file_name.lower().endswith('.docx'):
                                mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                                texto = extract_text_from_docx(archivo_path)
                            elif file_name.lower().endswith('.xlsx'):
                                mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                                texto = extract_text_from_xlsx(archivo_path)

                            if buscar_termino(texto, consulta):
                                fecha_modificacion = datetime.fromtimestamp(os.path.getmtime(archivo_path)).strftime('%d/%m/%Y')
                                resultados.append({
                                    'nombre': file_name,
                                    'url': f"{settings.MEDIA_URL}documentos/{file_name}",
                                    'fecha': fecha_modificacion
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


import os
from datetime import datetime
import logging
from django.shortcuts import render

# Verifica si el archivo ya existe en la ruta de descarga.
def archivo_existe(ruta_descarga, nombre_archivo):
    archivo_path = os.path.join(ruta_descarga, nombre_archivo)
    return os.path.exists(archivo_path)

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

# En tu lógica actual, reemplaza la generación de la URL del archivo
def consulta_view(request):
    resultados = None
    cantidad_archivos = 0
    search_done = False

    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            search_done = True
            consulta = form.cleaned_data['consulta']
            origen = form.cleaned_data['origen']
            logger.info(f"Consulta: {consulta}, Origen: {origen}")
            resultados = []

            if origen == 'drive':
                # Código para buscar en Google Drive
                pass
            elif origen == 'local':
                archivos_dir = settings.ARCHIVOS_DIR
                for root, dirs, files in os.walk(archivos_dir):
                    for file_name in files:
                        try:
                            archivo_path = os.path.join(root, file_name)
                            mime_type = None
                            texto = ""

                            # Extraer texto según el tipo de archivo
                            if file_name.lower().endswith('.pdf'):
                                mime_type = 'application/pdf'
                                texto = extract_text_from_pdf(archivo_path)
                            elif file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                                mime_type = 'image/jpeg'
                                texto = extract_text_from_image(archivo_path)
                            elif file_name.lower().endswith('.docx'):
                                mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                                texto = extract_text_from_docx(archivo_path)
                            elif file_name.lower().endswith('.xlsx'):
                                mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                                texto = extract_text_from_xlsx(archivo_path)

                            # Si se encuentra el término en el texto
                            if buscar_termino(texto, consulta):
                                ruta_archivo = obtener_ruta_archivo(file_name)
                                if ruta_archivo:
                                    fecha_modificacion = datetime.fromtimestamp(os.path.getmtime(archivo_path)).strftime('%d/%m/%Y')
                                    resultados.append({
                                        'nombre': file_name,
                                        'url': ruta_archivo,
                                        'fecha': fecha_modificacion
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

# Nueva función: Descargar archivos desde Google Drive
def descargar_archivos_nube(request):
    try:
        # Obtener archivos de la carpeta de Google Drive
        drive_files = search_files_in_drive(settings.DRIVE_FOLDER_ID)
        service = get_drive_service()

        if not drive_files:
            logger.info("No se encontraron archivos en la carpeta de Google Drive.")
            # Redirigir a un template cuando no se encuentran archivos
            return render(request, 'documentos/sin_archivos.html')

        logger.info(f"Archivos encontrados: {drive_files}")

        # Ruta donde se almacenarán los archivos descargados
        ruta_descarga = os.path.join(settings.MEDIA_ROOT, 'documentos', 'descargados')
        if not os.path.exists(ruta_descarga):
            os.makedirs(ruta_descarga)

        archivos_descargados = []
        archivos_omitidos = []

        # Recorremos cada archivo en Google Drive
        for file in drive_files:
            try:
                file_id = file['id']
                file_name = file['name']
                file_data = download_file(service, file_id)  # Descargar archivo

                if file_data:
                    # Obtener la fecha de subida y formatearla
                    created_time = file.get('createdTime', '')

                    # Verificar si el campo 'createdTime' está vacío y asignar un valor predeterminado
                    if created_time:
                        try:
                            fecha_formateada = datetime.strptime(created_time, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y%m%d_%H%M%S")
                        except ValueError:
                            logger.error(f"Error al formatear la fecha {created_time}. Asignando 'Fecha desconocida'.")
                            fecha_formateada = "Fecha_desconocida"
                    else:
                        logger.warning(f"El archivo {file_name} no tiene 'createdTime'. Asignando 'Fecha desconocida'.")
                        fecha_formateada = "Fecha_desconocida"

                    # Obtener la extensión original del archivo
                    extension = os.path.splitext(file_name)[1]

                    # Crear un nombre único para el archivo usando el nombre original, fecha y los primeros 8 caracteres del ID de Google Drive
                    id_corto = file_id[:8]
                    nuevo_nombre = f"bethania-{fecha_formateada}-{id_corto}{extension}"

                    # Verificar si el archivo ya ha sido descargado
                    if archivo_existe(ruta_descarga, nuevo_nombre):
                        logger.info(f"El archivo {nuevo_nombre} ya existe. Omitiendo descarga.")
                        archivos_omitidos.append(nuevo_nombre)
                    else:
                        # Guardar el archivo sin cambiar su formato original
                        archivo_path = os.path.join(ruta_descarga, nuevo_nombre)
                        with open(archivo_path, 'wb') as archivo_local:
                            archivo_local.write(file_data)  # Escribir los bytes descargados
                        logger.info(f"Archivo {file_name} descargado exitosamente como {nuevo_nombre}.")
                        archivos_descargados.append(nuevo_nombre)

                else:
                    logger.error(f"No se pudo obtener el contenido del archivo {file_name}.")
            except Exception as e:
                logger.error(f"Error descargando archivo {file_name}: {e}")
                return render(request, 'documentos/error_descarga.html', {'mensaje_error': f"Error descargando archivo {file_name}: {e}"})

        # Redirigir a un template que muestre los resultados de la descarga
        return render(request, 'documentos/resumen_descarga.html', {
            'archivos_descargados': archivos_descargados,
            'archivos_omitidos': archivos_omitidos
        })
    except Exception as e:
        logger.error(f"Error en la descarga de archivos: {e}")
        return render(request, 'documentos/error_descarga.html', {'mensaje_error': f"Error en la descarga de archivos: {e}"})

# Verificación si es superadministrador
def es_superadministrador(user):
    """Verifica si el usuario es un superadministrador."""
    return user.is_superuser


# Nueva función: Vaciar la carpeta de Google Drive (solo para superadministradores)
@user_passes_test(es_superadministrador, login_url='/forbidden/')
def vaciar_carpeta_drive(request):
    try:
        service = get_drive_service()
        folder_id = settings.DRIVE_FOLDER_ID
        results = service.files().list(q=f"'{folder_id}' in parents").execute()
        files = results.get('files', [])

        if not files:
            # Si no hay archivos en la carpeta, redirigir al template de carpeta vacía
            return render(request, 'documentos/carpeta_vacia.html')

        for file in files:
            try:
                service.files().delete(fileId=file['id']).execute()
            except Exception as error:
                logger.error(f"Error al eliminar el archivo {file['name']}: {error}")

        # Si se vació la carpeta correctamente, redirigir al template de éxito
        return render(request, 'documentos/carpeta_vaciada_exito.html')
    except Exception as e:
        logger.error(f"Error vaciando la carpeta: {e}")
        return HttpResponse(f"Error vaciando la carpeta: {e}")

def forbidden_view(request):
    """Muestra un mensaje de error cuando el usuario no tiene permisos suficientes."""
    return render(request, 'forbidden.html')
"""
# Función: Vaciar la carpeta de Google Drive (sin ser administrador)
def vaciar_carpeta_drive(request):
    try:
        service = get_drive_service()
        folder_id = settings.DRIVE_FOLDER_ID
        results = service.files().list(q=f"'{folder_id}' in parents").execute()
        files = results.get('files', [])

        for file in files:
            try:
                service.files().delete(fileId=file['id']).execute()
            except Exception as error:
                logger.error(f"Error al eliminar el archivo {file['name']}: {error}")

        return JsonResponse({'mensaje': 'Carpeta vaciada correctamente.'})
    except Exception as e:
        logger.error(f"Error vaciando la carpeta: {e}")
        return HttpResponse(f"Error vaciando la carpeta: {e}")
"""
