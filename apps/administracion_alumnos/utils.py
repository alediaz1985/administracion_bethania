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


# ====== Helpers PDFs / Institución (agregar al final de utils.py) ======
import os
from io import BytesIO
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Image, Paragraph, Table, TableStyle
from reportlab.lib.units import cm, inch
from PIL import Image as PilImage

def env_text(key, default=""):
    v = os.getenv(key, "").strip()
    return v if v else default

def get_institucion():
    return {
        "Nombre": env_text("INSTITUCION_NOMBRE", "Institución"),
        "Dirección": env_text("INSTITUCION_DIRECCION", ""),
        "Teléfono": env_text("INSTITUCION_TELEFONO", ""),
        "Email": env_text("INSTITUCION_EMAIL", ""),
    }

def _resolve_env_path(key, default_rel=""):
    raw = os.getenv(key, "").strip()
    if raw:
        return raw if os.path.isabs(raw) else os.path.join(settings.BASE_DIR, raw)
    if default_rel:
        return os.path.join(settings.BASE_DIR, default_rel)
    return ""

def get_logo_path():
    # 1) .env -> INSTITUCION_LOGO_PATH; 2) <BASE_DIR>/static/img/logo.png
    p = _resolve_env_path("INSTITUCION_LOGO_PATH", "static/img/logo.png")
    return p

def get_fotos_dir():
    # 1) .env -> INSTITUCION_FOTO_DIR; 2) <MEDIA_ROOT>/documentos/fotoPerfilEstudiante
    raw = os.getenv("INSTITUCION_FOTO_DIR", "").strip()
    if raw:
        return raw if os.path.isabs(raw) else os.path.join(settings.BASE_DIR, raw)
    return os.path.join(settings.MEDIA_ROOT, "documentos", "fotoPerfilEstudiante")

def styleset():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Small", fontSize=9, leading=11))
    return styles

def table_style_base():
    return TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ])

def table_style_header():
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3d3d3d")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ])

def logo_flowable(styles):
    path = get_logo_path()
    try:
        if path and os.path.exists(path):
            return Image(path, 1 * inch, 1 * inch)
    except Exception:
        pass
    return Paragraph("Logo no disponible", styles['Normal'])

def _crop_center_square(im: PilImage.Image) -> PilImage.Image:
    w, h = im.size
    if w == h: return im
    if w > h:
        left = (w - h) // 2
        return im.crop((left, 0, left + h, h))
    top = (h - w) // 2
    return im.crop((0, top, w, top + w))

def foto_estudiante_flowable(foto_ref: str | None, styles):
    """
    Busca la foto del alumno:
    - Si foto_ref contiene 'id=...', usa ese ID para buscar un archivo local que empiece con ese ID.
    - Redimensiona a 4x4 cm y devuelve un Flowable Image; si no hay, un Paragraph fallback.
    """
    if not foto_ref:
        return Paragraph("Foto no disponible", styles['Normal'])

    txt = str(foto_ref)
    foto_id = txt.split("id=")[-1].strip() if "id=" in txt else ""

    base_dir = get_fotos_dir()
    if not os.path.isdir(base_dir):
        return Paragraph("Foto no disponible", styles['Normal'])

    extensiones = ('.jpg', '.jpeg', '.png')
    try:
        for archivo in os.listdir(base_dir):
            nombre, ext = os.path.splitext(archivo)
            if ext.lower() not in extensiones:
                continue
            if foto_id and archivo.startswith(foto_id):
                ruta = os.path.join(base_dir, archivo)
                try:
                    with PilImage.open(ruta) as im:
                        im = im.convert("RGB")
                        im = _crop_center_square(im)
                        im = im.resize((int(4 * cm), int(4 * cm)))
                        bio = BytesIO()
                        im.save(bio, format="PNG")
                        bio.seek(0)
                        return Image(bio, width=4 * cm, height=4 * cm)
                except Exception:
                    return Paragraph("Foto no disponible", styles['Normal'])
        return Paragraph("Foto no disponible", styles['Normal'])
    except Exception:
        return Paragraph("Foto no disponible", styles['Normal'])

def fmt(v):  # str seguro
    return "" if v is None else str(v)

def fmt_bool(v):
    if v is None or v == "": return ""
    s = str(v).strip().lower()
    if s in ("si", "sí", "true", "1"): return "Sí"
    if s in ("no", "false", "0"): return "No"
    return str(v)
