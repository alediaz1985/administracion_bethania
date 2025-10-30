# apps/comprobantes/services.py
from __future__ import annotations
import hashlib
from io import BytesIO
from typing import Dict, Tuple

from django.core.files.base import ContentFile
from django.utils import timezone
from django.conf import settings
from googleapiclient.http import MediaIoBaseDownload

from apps.comprobantes.google_drive import get_drive_service  # usás el TUYO existente
from apps.administracion_alumnos.models import Estudiante, Responsable
from .models import Documento
from .utils import extract_drive_file_id, normalize_cuil, parse_timestamp_es

def _download_drive_file_bytes(file_id: str) -> Tuple[bytes, dict]:
    service = get_drive_service()
    meta = service.files().get(
        fileId=file_id,
        fields="id,name,mimeType,size,webViewLink,parents"
    ).execute()

    request = service.files().get_media(fileId=file_id)
    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    data = fh.getvalue()
    return data, meta

def _sha256(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def process_sheet_row(row: Dict[str, str]) -> Tuple[Documento | None, str]:
    """
    row -> dict por nombre de columna (encabezado del Sheet):
    - 'Marca temporal'
    - 'Dirección de correo electrónico'
    - 'adjunte el comprobante de pagos'
    - 'Ingrese el Cuil del Alumno'
    - 'Ingrese el Cuil del Responsable de Pago'
    """
    ts = parse_timestamp_es(row.get("Marca temporal"))
    correo = (row.get("Dirección de correo electrónico") or "").strip()
    link = (row.get("adjunte el comprobante de pagos") or "").strip()
    cuil_al = normalize_cuil(row.get("Ingrese el Cuil del Alumno"))
    if len(cuil_al) != 11:
        return None, f"CUIL de alumno inválido: {cuil_al}"

    cuil_rp = normalize_cuil(row.get("Ingrese el Cuil del Responsable de Pago"))
    if len(cuil_rp) != 11:
        return None, f"CUIL de responsable inválido: {cuil_rp}"

    file_id = extract_drive_file_id(link)
    if not file_id:
        return None, "No se pudo extraer el fileId del Drive."

    try:
        est = Estudiante.objects.get(cuil_estudiante=cuil_al)
    except Estudiante.DoesNotExist:
        return None, f"Estudiante CUIL {cuil_al} no existe."

    try:
        resp = Responsable.objects.get(cuil=cuil_rp)
    except Responsable.DoesNotExist:
        return None, f"Responsable CUIL {cuil_rp} no existe."

    # evitar duplicado por id
    existing = Documento.objects.filter(drive_file_id=file_id).first()
    if existing:
        existing.estado = "omitido"
        existing.error_msg = ""
        existing.procesado_en = timezone.now()
        existing.save(update_fields=["estado", "error_msg", "procesado_en"])
        return existing, ""

    # descargar
    data, meta = _download_drive_file_bytes(file_id)
    digest = _sha256(data)
    size = int(meta.get("size") or 0)

    doc = Documento(
        correo=correo,
        timestamp_form=ts,
        drive_file_id=file_id,
        drive_folder_id=(meta.get("parents") or [""])[0] if meta.get("parents") else "",
        drive_mime_type=meta.get("mimeType") or "",
        drive_web_view_link=meta.get("webViewLink") or "",
        original_filename=meta.get("name") or "",
        estudiante=est,
        cuil_estudiante=cuil_al,
        responsable=resp,
        cuil_responsable=cuil_rp,
        tamano_bytes=size,
        sha256=digest,
        estado="ok",
        procesado_en=timezone.now(),
    )
    # Guardar con NOMBRE = fileId (sin extensión), como pediste:
    doc.archivo.save(file_id, ContentFile(data), save=False)
    doc.save()
    return doc, ""
