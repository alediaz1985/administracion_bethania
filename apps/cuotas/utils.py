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


from mimetypes import guess_extension

def descargar_comprobante_drive(url):
    file_id = extraer_id_drive(url)
    print(f"[DEBUG] URL: {url}")
    print(f"[DEBUG] File ID extraído: {file_id}")

    if not file_id:
        print("[ERROR] No se pudo extraer el ID.")
        return None

    # Crear carpeta si no existe
    os.makedirs(CARPETA_DESTINO, exist_ok=True)

    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build("drive", "v3", credentials=creds)

    # Obtener metadatos para conocer el MIME type
    file_metadata = service.files().get(fileId=file_id, fields="mimeType, name").execute()
    mime_type = file_metadata.get("mimeType")
    original_name = file_metadata.get("name")

    print(f"[DEBUG] MIME type: {mime_type}")
    print(f"[DEBUG] Nombre original: {original_name}")

    # Determinar la extensión
    extension = guess_extension(mime_type) or '.bin'

    # Si guess_extension no devuelve algo útil, usar el nombre original
    if not extension or extension == '.ksh':  # Algunos casos fallan
        extension = os.path.splitext(original_name)[-1]

    # Crear nombre final con extensión correcta
    filename = f"{file_id}{extension}"
    ruta_absoluta = os.path.join(CARPETA_DESTINO, filename)
    ruta_relativa = os.path.join('documentos', 'comprobantes', filename)

    if os.path.exists(ruta_absoluta):
        print(f"[INFO] Ya existe: {ruta_absoluta}")
        return ruta_relativa

    # Descargar archivo
    print("[INFO] Descargando...")

    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(ruta_absoluta, 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"[INFO] Progreso: {int(status.progress() * 100)}%")

    print(f"[SUCCESS] Descargado en: {ruta_absoluta}")
    return ruta_relativa

