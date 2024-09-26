import os
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from django.conf import settings

# Define el TOKEN_PATH usando settings.BASE_DIR
TOKEN_PATH = os.path.join(settings.BASE_DIR, 'token.json')

# Configuración del logger
logger = logging.getLogger(__name__)

# Scope requerido para la gestión completa de Google Drive (incluye eliminación)
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    """Obtiene el servicio autenticado de Google Drive usando el token"""
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Si no hay token, iniciamos el flujo de autenticación
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.GOOGLE_CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)
            # Guardamos el token en un archivo
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as error:
        logger.error(f"Error al construir el servicio de Google Drive: {error}")
        return None

def asignar_permisos(service, file_id, email_user):
    """Asigna permisos de escritura a la cuenta para un archivo."""
    try:
        permisos = {
            'type': 'user',
            'role': 'writer',  # El rol 'writer' permite eliminar el archivo
            'emailAddress': email_user  # Correo electrónico de la cuenta que va a recibir los permisos
        }
        service.permissions().create(
            fileId=file_id,
            body=permisos,
            fields='id'
        ).execute()
        logger.info(f"Permisos de escritura otorgados para {email_user} en el archivo {file_id}")
    except Exception as e:
        logger.error(f"Error al otorgar permisos al archivo {file_id}: {e}")

# Función para eliminar archivos de una carpeta de Google Drive
def vaciar_carpeta_drive(folder_id):
    try:
        service = get_drive_service()
        if not service:
            return "Error al autenticar con Google Drive"

        # Listar todos los archivos en la carpeta
        archivos = service.files().list(q=f"'{folder_id}' in parents").execute().get('files', [])

        if not archivos:
            logger.info("No se encontraron archivos en la carpeta de Google Drive.")
            return "No se encontraron archivos en la carpeta."

        # Eliminar todos los archivos encontrados
        for archivo in archivos:
            file_id = archivo['id']
            service.files().delete(fileId=file_id).execute()
            logger.info(f"Archivo {archivo['name']} eliminado exitosamente.")

        return "Todos los archivos fueron eliminados exitosamente."
    except Exception as e:
        logger.error(f"Error vaciando la carpeta de Google Drive: {e}")
        return f"Error vaciando la carpeta: {e}"

def descargar_archivo(service, file_id, nombre_archivo, ruta_descarga):
    """Descarga un archivo desde Google Drive."""
    try:
        request = service.files().get_media(fileId=file_id)
        archivo_path = os.path.join(ruta_descarga, nombre_archivo)
        with open(archivo_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                logger.info(f"Descargando {nombre_archivo}: {int(status.progress() * 100)}%.")
        logger.info(f"Archivo {nombre_archivo} descargado correctamente.")
    except Exception as e:
        logger.error(f"Error al descargar el archivo {nombre_archivo}: {e}")

def listar_archivos_en_carpeta(service, folder_id):
    """Lista todos los archivos en una carpeta de Google Drive."""
    try:
        archivos = service.files().list(q=f"'{folder_id}' in parents").execute().get('files', [])
        if not archivos:
            logger.info("No se encontraron archivos en la carpeta.")
            return []
        return archivos
    except Exception as e:
        logger.error(f"Error al listar los archivos de la carpeta {folder_id}: {e}")
        return []

def search_files_in_drive(folder_id):
    """Busca archivos en una carpeta de Google Drive."""
    service = get_drive_service()
    try:
        archivos = service.files().list(q=f"'{folder_id}' in parents").execute().get('files', [])
        if not archivos:
            logger.info("No se encontraron archivos en la carpeta de Google Drive.")
            return []
        return archivos
    except HttpError as error:
        logger.error(f"An error occurred: {error}")
        return []

def download_file(service, file_id):
    """Descarga el contenido de un archivo en Google Drive."""
    try:
        request = service.files().get_media(fileId=file_id)
        file_data = request.execute()
        return file_data
    except HttpError as error:
        logger.error(f"An error occurred: {error}")
        return None

def extract_text_from_file(file_data, mime_type):
    """Extrae texto del archivo según su tipo MIME."""
    # Implementación para extraer texto según el tipo de archivo (PDF, imagen, DOCX, etc.)
    pass  # Aquí puedes agregar la lógica que tenías para extraer el texto
