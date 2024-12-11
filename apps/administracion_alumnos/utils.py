import os
import logging

logger = logging.getLogger(__name__)

def search_files_in_drive(folder_id, service):
    """Busca archivos en una carpeta específica de Google Drive."""
    try:
        query = f"'{folder_id}' in parents and trashed=false"
        results = service.files().list(q=query, fields="files(id, name, createdTime)").execute()
        return results.get('files', [])
    except Exception as e:
        logger.error(f"Error buscando archivos en Google Drive: {e}")
        return []

def download_file(service, file_id):
    """Descarga el contenido de un archivo desde Google Drive."""
    try:
        request = service.files().get_media(fileId=file_id)
        file_data = request.execute()
        return file_data
    except Exception as e:
        logger.error(f"Error descargando archivo con ID {file_id}: {e}")
        return None

def archivo_existe(ruta, nombre_archivo):
    """Verifica si un archivo ya existe en una ruta específica."""
    return os.path.exists(os.path.join(ruta, nombre_archivo))
