import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload

def get_drive_service():
    """
    Devuelve el servicio de Google Drive autenticado.
    """
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = service_account.Credentials.from_service_account_file(
        'cuotas/credentials.json', scopes=SCOPES)  # Ruta al archivo de credenciales
    service = build('drive', 'v3', credentials=creds)
    return service

def download_file(service, file_id, file_name, download_folder):
    """
    Descarga el archivo desde Google Drive.
    """
    request = service.files().get_media(fileId=file_id)
    file_path = os.path.join(download_folder, file_name)

    with open(file_path, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

    return file_path
