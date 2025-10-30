from __future__ import annotations

import json
import os
import logging
from datetime import datetime
from typing import Any, Dict, List

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from django.http import JsonResponse

# views.py
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.shortcuts import redirect
from django.conf import settings
from datetime import datetime
import logging

# Google Drive helpers (según tu módulo ya actualizado)
from .google_drive import (
    get_drive_service,
    search_files_in_drive,
    descargar_archivos_desde_carpeta,
    vaciar_carpeta_drive as gd_vaciar,
)

logger = logging.getLogger(__name__)


def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest" or request.GET.get("ajax") == "1"

# ============================================================
# HOME (panel único)
# ============================================================
def home_comprobantes(request: HttpRequest) -> HttpResponse:
    """
    Panel principal. Muestra orígenes y resultados de las acciones.
    Lee resultados desde request.session y los limpia luego de mostrarlos.
    """
    sources: Dict[str, Dict[str, str]] = getattr(settings, "DRIVE_SOURCES", {})

    ctx = {
        "sources": sources,
        "resultado_sync": request.session.pop("resultado_sync", None),
        "resultado_vaciar": request.session.pop("resultado_vaciar", None),
        "resultado_list_files": request.session.pop("resultado_list_files", None),
        "resultado_consulta": request.session.pop("resultado_consulta", None),
        "resultado_subida": request.session.pop("resultado_subida", None),
        "ahora": datetime.now(),
    }
    return render(request, "comprobantes/home.html", ctx)


# ============================================================
# LISTAR ARCHIVOS (en Drive)  -> muestra en home
# ============================================================
def list_files(request: HttpRequest) -> HttpResponse:
    """
    Lista archivos de una carpeta de Drive por 'label' o por DRIVE_FOLDER_ID (compat).
    Deja el resultado en sesión y vuelve al panel.
    """
    label = request.GET.get("label")
    sources = getattr(settings, "DRIVE_SOURCES", {})
    files: List[Dict[str, Any]] = []
    folder_id = None
    error = None

    try:
        service = get_drive_service()
        if not service:
            raise RuntimeError("No se pudo autenticar Google Drive.")

        if label and label in sources and sources[label].get("folder_id"):
            folder_id = sources[label]["folder_id"]
        else:
            # Compatibilidad: usa un folder único si lo tuvieras
            folder_id = getattr(settings, "DRIVE_FOLDER_ID", "")
            if not folder_id:
                raise RuntimeError("No se indicó ?label ni existe DRIVE_FOLDER_ID.")

        resp = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields="files(id,name,mimeType,modifiedTime,createdTime)"
        ).execute()
        files = resp.get("files", [])
    except Exception as e:
        logger.error(f"[list_files] {e}")
        error = str(e)

    request.session["resultado_list_files"] = {
        "label": label or "default",
        "folder_id": folder_id or "",
        "files": files,
        "error": error,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }

    payload = {
        "tipo": "list_files",
        "label": label or "default",
        "folder_id": folder_id or "",
        "files": files,
        "error": error,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }


logger = logging.getLogger(__name__)

def _is_ajax(request: HttpRequest) -> bool:
    """Detecta si el request vino por AJAX (fetch)."""
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"

def descargar_archivos_nube(request: HttpRequest) -> HttpResponse:
    """
    Descarga los archivos desde la carpeta de Drive indicada.
    Si viene por AJAX => devuelve JSON con resultado.
    Si no => redirige a la vista de resumen.
    """
    label = request.GET.get("label")
    sources = getattr(settings, "DRIVE_SOURCES", {})

    folder_id = None
    resultado = {"descargados": [], "omitidos": [], "errores": []}

    try:
        # Determinar carpeta origen
        if label and label in sources and sources[label].get("folder_id"):
            folder_id = sources[label]["folder_id"]
        else:
            folder_id = getattr(settings, "DRIVE_FOLDER_ID", "")

        if not folder_id:
            raise RuntimeError("No hay carpeta configurada para la descarga.")

        # === AQUÍ DEBES USAR tu función que realmente baja archivos ===
        # Ejemplo:
        # resultado = descargar_archivos_desde_carpeta(folder_id)
        resultado = {
            "descargados": ["ejemplo1.pdf", "ejemplo2.xml"],
            "omitidos": ["ya_existente.pdf"],
            "errores": []
        }

        # Guardar resumen en sesión
        request.session["resultado_sync"] = {
            "label": label or "default",
            "folder_id": folder_id,
            "descargados": resultado["descargados"],
            "omitidos": resultado["omitidos"],
            "errores": resultado["errores"],
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }

    except Exception as e:
        logger.error(f"[descargar_archivos_nube] {e}")
        request.session["resultado_sync"] = {
            "label": label or "default",
            "folder_id": folder_id or "",
            "descargados": [],
            "omitidos": [],
            "errores": [str(e)],
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }

    payload = {
        "tipo": "descarga",
        "label": label or "default",
        "folder_id": folder_id or "",
        "descargados": request.session["resultado_sync"]["descargados"],
        "omitidos": request.session["resultado_sync"]["omitidos"],
        "errores": request.session["resultado_sync"]["errores"],
        "fecha": request.session["resultado_sync"]["fecha"],
    }

    # === Si es AJAX => devolver JSON, si no => redirect ===
    if _is_ajax(request):
        return JsonResponse(payload, status=200)

    return redirect("comprobantes:exito_descarga")

# ============================================================
# VACIAR CARPETA EN DRIVE -> muestra en home
# ============================================================
def vaciar_carpeta_drive(request: HttpRequest) -> HttpResponse:
    """
    Vacía una carpeta de Drive por 'label'. Guarda el mensaje en sesión y vuelve al home.
    """
    label = request.GET.get("label")
    sources = getattr(settings, "DRIVE_SOURCES", {})

    folder_id = ""
    mensaje = "Falta ?label o no existe en DRIVE_SOURCES."

    try:
        if label and label in sources and sources[label].get("folder_id"):
            folder_id = sources[label]["folder_id"]
            mensaje = gd_vaciar(folder_id)
    except Exception as e:
        logger.error(f"[vaciar_carpeta_drive] {e}")
        mensaje = f"Error: {e}"

    request.session["resultado_vaciar"] = {
        "label": label or "desconocido",
        "folder_id": folder_id,
        "mensaje": mensaje,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }

    payload = {
        "tipo": "vaciar",
        "label": label or "desconocido",
        "folder_id": folder_id,
        "mensaje": mensaje,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
    if _is_ajax(request):
        return JsonResponse(payload, status=200)
    request.session["resultado_vaciar"] = payload
    return redirect("comprobantes:home")

# ============================================================
# CONSULTA SIMPLE (local o Drive) -> según necesidad
# ============================================================
def consulta_view(request: HttpRequest) -> HttpResponse:
    """
    Consulta simple por nombre (contiene) sobre archivos ya descargados en MEDIA_ROOT.
    - Parámetros: q (texto), label (opcional).
    - Busca en: MEDIA_ROOT/<dest_subpath>/<label> si existe label; o en todos los dest_subpath.
    Deja resultado en sesión y vuelve al home.
    """
    q = (request.GET.get("q") or "").strip()
    label = request.GET.get("label")

    results: List[Dict[str, str]] = []
    error = None

    try:
        if not q:
            raise ValueError("Ingresá un término de búsqueda (?q=).")

        # Armamos rutas de búsqueda según DRIVE_SOURCES
        sources = getattr(settings, "DRIVE_SOURCES", {})
        base_media = str(settings.MEDIA_ROOT)

        # Si se pasa label: solo esa
        to_scan: List[str] = []
        if label and label in sources:
            sub = sources[label].get("dest_subpath", "documentos/descargados")
            to_scan.append(os.path.join(base_media, sub, label))
        else:
            # Todas las configuradas
            for lbl, cfg in sources.items():
                sub = cfg.get("dest_subpath", "documentos/descargados")
                to_scan.append(os.path.join(base_media, sub, lbl))

        # Recorremos
        for root in to_scan:
            if not os.path.exists(root):
                continue
            for fname in os.listdir(root):
                if q.lower() in fname.lower():
                    results.append({
                        "archivo": fname,
                        "ruta": root,
                        "label": label or "varios",
                    })

    except Exception as e:
        logger.error(f"[consulta_view] {e}")
        error = str(e)

    request.session["resultado_consulta"] = {
        "q": q,
        "label": label or "todos",
        "resultados": results,
        "error": error,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
    payload = {
        "tipo": "consulta",
        "q": q,
        "label": label or "todos",
        "resultados": results,
        "error": error,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
    if _is_ajax(request):
        return JsonResponse(payload, status=200)
    request.session["resultado_consulta"] = payload
    return redirect("comprobantes:home")


# ============================================================
# CONSULTA COMPROBANTES (placeholder específico)
# ============================================================
def consulta_comprobantes(request: HttpRequest) -> HttpResponse:
    """
    Consulta específica de comprobantes. Podés adaptar a tus modelos.
    Por ahora, reusa la misma consulta simple local con label='comprobantes'.
    """
    # Redirige a la consulta general forzando label=comprobantes
    q = request.GET.get("q", "")
    url = f"{reverse('comprobantes:consulta')}?q={q}&label=comprobantes"
    return redirect(url)


# ============================================================
# SUBIR COMPROBANTE (carga manual local) -> muestra en home
# ============================================================
def subir_comprobante(request: HttpRequest) -> HttpResponse:
    """
    Sube un archivo manualmente al servidor (no a Drive).
    Guarda en MEDIA_ROOT/documentos/comprobantes/subidos/.
    Deja resultado en sesión y vuelve al home.
    """
    if request.method == "POST":
        archivo = request.FILES.get("archivo")
        error = None
        saved_path = ""
        try:
            if not archivo:
                raise ValueError("No se envió ningún archivo.")

            # Destino local
            dest_rel = os.path.join("documentos", "comprobantes", "subidos")
            dest_abs = os.path.join(str(settings.MEDIA_ROOT), dest_rel)
            os.makedirs(dest_abs, exist_ok=True)

            # Guardar con nombre seguro
            nombre = archivo.name
            final_path = os.path.join(dest_abs, nombre)
            with default_storage.open(final_path, "wb+") as dst:
                for chunk in archivo.chunks():
                    dst.write(chunk)
            saved_path = final_path

        except Exception as e:
            logger.error(f"[subir_comprobante] {e}")
            error = str(e)

        request.session["resultado_subida"] = {
            "archivo": archivo.name if 'archivo' in locals() and archivo else "",
            "ruta": saved_path,
            "error": error,
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
        return redirect("comprobantes:home")

    # Si es GET, renderizar un formulario básico (o usá modal en home)
    return render(request, "comprobantes/subir_comprobante.html", {})


# ============================================================
# ÉXITO DESCARGA (si lo seguís usando en algún lado)
# ============================================================
def exito_descarga(request: HttpRequest) -> HttpResponse:
    """
    Vista simple por compatibilidad. Podés seguir redirigiendo al home si querés.
    """
    return render(request, "comprobantes/exito_descarga.html", {"fecha": datetime.now()})



#--------------------------------------------------------------------------------------------
