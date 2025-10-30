# apps/comprobantes/views_import_sheet.py
from __future__ import annotations
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings

from .google_sheets import get_sheets_service
from .services import process_sheet_row

# Columnas esperadas exactamente como llegan desde el Form
HEADERS_ES = [
    "Marca temporal",
    "Dirección de correo electrónico",
    "adjunte el comprobante de pagos",
    "Ingrese el Cuil del Alumno",
    "Ingrese el Cuil del Responsable de Pago",
]

def importar_comprobantes_desde_sheet_auth(request: HttpRequest) -> HttpResponse:
    """
    Lee Google Sheets con credenciales (Service Account) y procesa filas.
    Parámetros:
      - sheet_id: opcional (usa settings.COMPROBANTES_SHEET_ID si no viene)
      - range:    opcional A1 notation, ej: 'Respuestas de formulario 1'!A:E
                  si no viene, usa settings.COMPROBANTES_SHEET_RANGE
    """
    sheet_id = request.GET.get("sheet_id") or getattr(settings, "COMPROBANTES_SHEET_ID", "")
    rng = request.GET.get("range") or getattr(settings, "COMPROBANTES_SHEET_RANGE", "A:E")
    tab = getattr(settings, "COMPROBANTES_SHEET_TAB", "")

    if not sheet_id:
        return JsonResponse({"error": "Falta COMPROBANTES_SHEET_ID o ?sheet_id="}, status=400)

    a1 = f"'{tab}'!{rng}" if tab else rng

    service = get_sheets_service()
    sheet = service.spreadsheets()
    res = sheet.values().get(spreadsheetId=sheet_id, range=a1).execute()
    values = res.get("values", [])

    if not values:
        payload = {"total": 0, "procesados": [], "omitidos": [], "errores": []}
        return JsonResponse(payload, status=200)

    headers = values[0]
    rows = values[1:]

    # Mapear columnas por nombre
    idx = {name: headers.index(name) for name in HEADERS_ES if name in headers}
    faltantes = [h for h in HEADERS_ES if h not in idx]
    if faltantes:
        return JsonResponse({"error": f"Faltan columnas en el Sheet: {', '.join(faltantes)}"}, status=400)

    procesados, omitidos, errores = [], [], []

    for v in rows:
        row = {
            "Marca temporal": v[idx["Marca temporal"]] if idx["Marca temporal"] < len(v) else "",
            "Dirección de correo electrónico": v[idx["Dirección de correo electrónico"]] if idx["Dirección de correo electrónico"] < len(v) else "",
            "adjunte el comprobante de pagos": v[idx["adjunte el comprobante de pagos"]] if idx["adjunte el comprobante de pagos"] < len(v) else "",
            "Ingrese el Cuil del Alumno": v[idx["Ingrese el Cuil del Alumno"]] if idx["Ingrese el Cuil del Alumno"] < len(v) else "",
            "Ingrese el Cuil del Responsable de Pago": v[idx["Ingrese el Cuil del Responsable de Pago"]] if idx["Ingrese el Cuil del Responsable de Pago"] < len(v) else "",
        }
        doc, err = process_sheet_row(row)
        if err:
            errores.append({"file": row.get("adjunte el comprobante de pagos"), "error": err})
        elif doc and doc.estado == "omitido":
            omitidos.append(doc.drive_file_id)
        elif doc:
            procesados.append(doc.drive_file_id)

    payload = {
        "total": len(procesados) + len(omitidos) + len(errores),
        "procesados": procesados,
        "omitidos": omitidos,
        "errores": errores,
    }

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(payload, status=200)

    request.session["resultado_sync"] = payload
    messages.success(request, f"Importación: {len(procesados)} nuevos, {len(omitidos)} omitidos, {len(errores)} errores.")
    return redirect("comprobantes:home")
