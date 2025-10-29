from celery import shared_task
from .google_drive import download_file, extract_text_from_file, get_drive_service
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_file_task(file, consulta):
    try:
        service = get_drive_service()
        file_id = file['id']
        file_name = file['name']
        mime_type = file['mimeType']
        created_time = file['createdTime']
        web_view_link = file.get('webViewLink', '#')
        file_data = download_file(service, file_id)
        if file_data:
            texto = extract_text_from_file(file_data, mime_type)
            print(f"Texto extraído de {file_name}: {texto[:500]}")  # Mostrar los primeros 500 caracteres para depuración
            if consulta.lower() in texto.lower():
                return {
                    'nombre': file_name,
                    'url': web_view_link,
                    'fecha': created_time
                }
    except Exception as e:
        logger.error(f"Error procesando archivo {file_name}: {e}")
        print(f"Error procesando archivo {file_name}: {e}")
    return None
