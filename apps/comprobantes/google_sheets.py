# apps/comprobantes/google_sheets.py
from __future__ import annotations
import os
from django.conf import settings
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

def get_sheets_service():
    """
    Crea un cliente de Google Sheets API usando el mismo credentials.json
    que usás para Drive. Asegurate de compartir el Sheet con el client_email
    de estas credenciales (si es Service Account).
    """
    cred_path = getattr(settings, "GOOGLE_CREDENTIALS", "apps/comprobantes/credentials.json")
    cred_path = os.path.join(settings.BASE_DIR, cred_path) if not os.path.isabs(cred_path) else cred_path

    credentials = service_account.Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    return build("sheets", "v4", credentials=credentials)
