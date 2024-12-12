import os
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# Ruta de credenciales
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOOGLE_CREDENTIALS = os.path.join(BASE_DIR, 'documentos', 'credentials.json')  # Ajuste del nombre del archivo
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_drive():
    """
    Autentica con Google Drive utilizando un archivo de credenciales de servicio.

    Retorna:
        service (googleapiclient.discovery.Resource): Objeto de servicio de Google Drive.
    """
    # Verificar si el archivo de credenciales existe
    print(f"Ruta calculada: {GOOGLE_CREDENTIALS}")
    if not os.path.exists(GOOGLE_CREDENTIALS):
        raise FileNotFoundError(f"El archivo de credenciales no se encuentra en: {GOOGLE_CREDENTIALS}")

    # Autenticar con las credenciales
    credentials = Credentials.from_service_account_file(GOOGLE_CREDENTIALS, scopes=SCOPES)

    # Crear el servicio de Google Drive
    service = build('drive', 'v3', credentials=credentials)
    return service
