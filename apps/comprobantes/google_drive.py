import os
import re
import logging
from typing import Dict, List
from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

# ---- Config
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
GOOGLE_CREDENTIALS = getattr(settings, "GOOGLE_CREDENTIALS", "apps/comprobantes/credentials.json")
if not os.path.isabs(GOOGLE_CREDENTIALS):
    GOOGLE_CREDENTIALS = str((settings.BASE_DIR / GOOGLE_CREDENTIALS).resolve())

# ---- Auth
def get_drive_service():
    """Servicio Drive autenticado (Service Account)."""
    try:
        if not os.path.exists(GOOGLE_CREDENTIALS):
            raise FileNotFoundError(f"No se encontró el archivo de credenciales: {GOOGLE_CREDENTIALS}")
        creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS, scopes=SCOPES)
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        logger.error(f"Error autenticando Google Drive: {e}")
        return None

# ---- Utils
_GOOGLE_APPS_PREFIX = "application/vnd.google-apps"
EXPORT_MAP = {
    "application/vnd.google-apps.document": ("application/pdf", ".pdf"),
    "application/vnd.google-apps.spreadsheet": ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"),
    "application/vnd.google-apps.presentation": ("application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx"),
}

def _sanitize(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]+', "_", name).strip() or "archivo"

def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def _build_path(dest_root: str, file_id: str, name: str, ext: str = "") -> str:
    base = _sanitize(name)
    if ext and not base.lower().endswith(ext.lower()):
        base = f"{base}{ext}"
    return os.path.join(dest_root, f"{file_id}_{base}")

def _iter_folder_files(service, folder_id: str):
    page_token = None
    while True:
        resp = (
            service.files()
            .list(
                q=f"'{folder_id}' in parents and trashed = false",
                fields="nextPageToken, files(id,name,mimeType,modifiedTime)",
                pageToken=page_token,
            )
            .execute()
        )
        for f in resp.get("files", []):
            yield f
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

# ---- API que usan tus views

def search_files_in_drive(folder_id: str):
    """Devuelve lista de archivos (id, name, createdTime, mimeType) de una carpeta."""
    try:
        service = get_drive_service()
        if not service:
            return []
        response = (
            service.files()
            .list(
                q=f"'{folder_id}' in parents and trashed = false",
                fields="files(id,name,createdTime,mimeType)"
            )
            .execute()
        )
        return response.get("files", [])
    except HttpError as e:
        logger.error(f"Error buscando archivos: {e}")
        return []

def download_file(service, file_id: str, file_name: str, destination: str):
    """Descarga un archivo binario a destination/file_name (compat firma actual)."""
    try:
        path = os.path.join(destination, file_name)
        req = service.files().get_media(fileId=file_id)
        with open(path, "wb") as fh:
            dl = MediaIoBaseDownload(fh, req)
            done = False
            while not done:
                status, done = dl.next_chunk()
                if status:
                    logger.info(f"Descargando {file_name}: {int(status.progress()*100)}%")
        return path
    except Exception as e:
        logger.error(f"Error descargando {file_name}: {e}")
        return None

def descargar_archivos_desde_carpeta(folder_id: str) -> Dict[str, List[str]]:
    """
    Descarga/exporta todo desde una carpeta de Drive a MEDIA_ROOT/<dest_subpath>/<label>/ID_nombre.ext
    Retorna {'descargados': [], 'omitidos': [], 'errores': []}
    """
    resultados = {"descargados": [], "omitidos": [], "errores": []}
    try:
        service = get_drive_service()
        if not service:
            resultados["errores"].append("Error autenticando Google Drive.")
            return resultados

        # deducir label y subcarpeta
        label = None
        dest_subpath = "documentos/descargados"
        for lbl, cfg in getattr(settings, "DRIVE_SOURCES", {}).items():
            if cfg.get("folder_id") == folder_id:
                label = lbl
                dest_subpath = cfg.get("dest_subpath", dest_subpath)
                break

        dest_root = os.path.join(str(settings.MEDIA_ROOT), dest_subpath)
        if label:
            dest_root = os.path.join(dest_root, label)
        _ensure_dir(dest_root)

        for f in _iter_folder_files(service, folder_id):
            fid = f["id"]
            name = f["name"]
            mime = f.get("mimeType", "")

            try:
                if mime.startswith(_GOOGLE_APPS_PREFIX):
                    mime_export, ext = EXPORT_MAP.get(mime, ("application/pdf", ".pdf"))
                    path = _build_path(dest_root, fid, name, ext)
                    if os.path.exists(path):
                        resultados["omitidos"].append(os.path.basename(path))
                        continue
                    req = service.files().export_media(fileId=fid, mimeType=mime_export)
                else:
                    path = _build_path(dest_root, fid, name)
                    if os.path.exists(path):
                        resultados["omitidos"].append(os.path.basename(path))
                        continue
                    req = service.files().get_media(fileId=fid)

                with open(path, "wb") as fh:
                    dl = MediaIoBaseDownload(fh, req)
                    done = False
                    while not done:
                        status, done = dl.next_chunk()
                        if status:
                            logger.info(f"Descargando {os.path.basename(path)}: {int(status.progress()*100)}%")
                resultados["descargados"].append(os.path.basename(path))

            except HttpError as he:
                logger.error(f"HttpError {name} ({fid}): {he}")
                resultados["errores"].append(f"{name}: {he}")
            except Exception as e:
                logger.exception(f"Error con {name} ({fid})")
                resultados["errores"].append(f"{name}: {e}")

        return resultados
    except Exception as e:
        logger.error(f"Error general descargando carpeta: {e}")
        resultados["errores"].append(str(e))
        return resultados

def vaciar_carpeta_drive(folder_id: str):
    """Elimina todos los archivos en una carpeta de Drive."""
    try:
        service = get_drive_service()
        if not service:
            return "Error al autenticar con Google Drive"
        files = service.files().list(q=f"'{folder_id}' in parents and trashed = false", fields="files(id,name)").execute().get("files", [])
        if not files:
            return "No se encontraron archivos en la carpeta."
        for f in files:
            service.files().delete(fileId=f["id"]).execute()
            logger.info(f"Archivo {f['name']} eliminado.")
        return "Todos los archivos fueron eliminados exitosamente."
    except Exception as e:
        logger.error(f"Error vaciando la carpeta de Google Drive: {e}")
        return f"Error vaciando la carpeta: {e}"
