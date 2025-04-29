import os
import io
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from django.conf import settings

CREDENTIALS_FILE = settings.GOOGLE_CREDENTIALS

CARPETA_DESTINO = os.path.join(settings.MEDIA_ROOT, 'documentos', 'comprobantes')


def extraer_id_drive(url):
    """
    Extrae el ID de un archivo de Google Drive desde una URL.
    """
    patron = r"id=([\w-]+)|/d/([\w-]+)"
    coincidencia = re.search(patron, url)
    return coincidencia.group(1) or coincidencia.group(2) if coincidencia else None


def descargar_comprobante_drive(url):
    file_id = extraer_id_drive(url)
    print(f"[DEBUG] URL: {url}")
    print(f"[DEBUG] File ID extraído: {file_id}")

    if not file_id:
        print("[ERROR] No se pudo extraer el ID.")
        return None

    # Crea la carpeta de destino si no existe
    os.makedirs(CARPETA_DESTINO, exist_ok=True)

    # Ruta absoluta para guardar el archivo físicamente
    ruta_absoluta = os.path.join(CARPETA_DESTINO, f"{file_id}.pdf")

    # Ruta relativa para guardar en la base de datos
    ruta_relativa = os.path.join('documentos', 'comprobantes', f"{file_id}.pdf")

    if os.path.exists(ruta_absoluta):
        print(f"[INFO] Ya existe: {ruta_absoluta}")
        return ruta_relativa  # ← Devolvemos la ruta RELATIVA

    print("[INFO] Descargando...")

    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build("drive", "v3", credentials=creds)

    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(ruta_absoluta, 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"[INFO] Progreso: {int(status.progress() * 100)}%")

    print(f"[SUCCESS] Descargado en: {ruta_absoluta}")
    return ruta_relativa  # ← Devolvemos la ruta RELATIVA
