from django.shortcuts import render, redirect
from django.conf import settings  # Importar settings para obtener MEDIA_ROOT y ARCHIVOS_DIR
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

# Configura el logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
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
    """Elimina caracteres no numéricos de un texto."""
    return re.sub(r'\D', '', texto)

def buscar_termino(texto, consulta):
    texto_limpio = limpiar_texto(texto)
    consulta_limpia = limpiar_texto(consulta)
    return consulta_limpia in texto_limpio

def consulta_view(request):
    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            consulta = form.cleaned_data['consulta']
            origen = form.cleaned_data['origen']
            logger.info(f"Consulta: {consulta}, Origen: {origen}")
            print(f"Consulta: {consulta}, Origen: {origen}")
            resultados = []

            if origen == 'drive':
                # Buscar archivos en la carpeta de Google Drive
                drive_files = search_files_in_drive(settings.DRIVE_FOLDER_ID)
                service = get_drive_service()

                if not drive_files:
                    logger.info("No se encontraron archivos en la carpeta de Google Drive.")
                    print("No se encontraron archivos en la carpeta de Google Drive.")
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
                                print(f"Texto extraído de {file_name}: {texto[:500]}")  # Mostrar los primeros 500 caracteres para depuración
                                if buscar_termino(texto, consulta):
                                    resultados.append({
                                        'nombre': file_name,
                                        'url': web_view_link,
                                        'fecha': created_time_formatted
                                    })
                                    logger.info(f"Término encontrado en: {file_name}")
                                    print(f"Término encontrado en: {file_name}")
                                else:
                                    logger.info(f"Término no encontrado en: {file_name}")
                                    print(f"Término no encontrado en: {file_name}")
                        except Exception as e:
                            logger.error(f"Error procesando archivo {file_name}: {e}")
                            print(f"Error procesando archivo {file_name}: {e}")
            elif origen == 'local':
                # Buscar archivos en la carpeta local
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
                                logger.info(f"Término encontrado en: {file_name}")
                                print(f"Término encontrado en: {file_name}")
                            else:
                                logger.info(f"Término no encontrado en: {file_name}")
                                print(f"Término no encontrado en: {file_name}")
                        except Exception as e:
                            logger.error(f"Error procesando archivo {file_name}: {e}")
                            print(f"Error procesando archivo {file_name}: {e}")

            return render(request, 'documentos/resultados.html', {'form': form, 'resultados': resultados, 'cantidad_archivos': len(resultados)})

    else:
        form = ConsultaForm()

    return render(request, 'documentos/consulta.html', {'form': form})

def subir_comprobante_view(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('consulta')
    else:
        form = DocumentoForm()
    return render(request, 'documentos/subir_comprobante.html', {'form': form})
