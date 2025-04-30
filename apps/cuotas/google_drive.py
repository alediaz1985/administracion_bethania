import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Ruta a las credenciales dentro de la app 'cuotas'
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'credentials.json')
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Error autenticando con Google Drive: {e}")
        return None
