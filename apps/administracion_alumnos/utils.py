import os
import logging
from django.conf import settings  # ✅ AGREGAR ESTA LÍNEA
from google.oauth2 import service_account
from googleapiclient.discovery import build

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

# 🧠 NUEVO: función para crear la conexión con Google Drive
def get_drive_service():
    """
    Autentica y devuelve el servicio de Google Drive.
    Usa el archivo de credenciales (service account JSON).
    """
    cred_path = os.path.join(settings.BASE_DIR, 'credenciales', 'credentials.json')

    if not os.path.exists(cred_path):
        raise FileNotFoundError(f"No se encontró el archivo de credenciales: {cred_path}")

    SCOPES = ['https://www.googleapis.com/auth/drive']

    creds = service_account.Credentials.from_service_account_file(
        cred_path, scopes=SCOPES
    )

    service = build('drive', 'v3', credentials=creds)
    return service