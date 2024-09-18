import os
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# Configurar el logging
logger = logging.getLogger(__name__)

# Scope requerido para la gestión completa de Google Drive (incluye eliminación)
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    """Autentica con Google Drive y devuelve el servicio."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build('drive', 'v3', credentials=creds)
    return service

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

def vaciar_carpeta_drive(folder_id):
    """Elimina todos los archivos de una carpeta en Google Drive."""
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
            try:
                file_id = archivo['id']
                try:
                    # Intentamos eliminar el archivo
                    service.files().delete(fileId=file_id).execute()
                    logger.info(f"Archivo {archivo['name']} eliminado exitosamente.")
                except HttpError as e:
                    # Si ocurre un error de permisos, intentamos asignar permisos de escritura
                    if 'insufficientFilePermissions' in str(e):
                        logger.warning(f"Permisos insuficientes para eliminar el archivo {archivo['name']}. Intentando asignar permisos...")
                        asignar_permisos(service, file_id, "tu_email@gmail.com")  # Aquí usa el correo de la cuenta de servicio o usuario autenticado
                        # Luego de asignar permisos, intentamos eliminar el archivo de nuevo
                        service.files().delete(fileId=file_id).execute()
                        logger.info(f"Archivo {archivo['name']} eliminado exitosamente tras otorgar permisos.")
                    else:
                        raise e
            except Exception as e:
                logger.error(f"Error eliminando archivo {archivo['name']}: {e}")

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
            while done is False:
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
