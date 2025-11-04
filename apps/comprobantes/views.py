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


from apps.comprobantes.models import ComprobantePago
from django.db.models import Q
from datetime import datetime, timedelta
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST

# ============================================================
# LISTA COMPROBANTES
# ============================================================
def lista_comprobantes(request):
    """
    Muestra los comprobantes de pago.
    Por defecto, no muestra nada hasta que el usuario aplique un filtro o elija "Ver todos".
    """
    comprobantes = None  # tabla vacía por defecto
    ver_todos = request.GET.get('ver_todos')

    # Si presiona "Ver todos" o usa algún filtro, traemos los registros
    if ver_todos or any(value for key, value in request.GET.items() if value):
        comprobantes = ComprobantePago.objects.select_related('estudiante').all()

        # Filtros
        buscar = request.GET.get('buscar', '').strip()
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        periodo = request.GET.get('periodo')
        estado = request.GET.get('estado')

        # 🔍 Buscar por CUIL estudiante o responsable
        if buscar:
            comprobantes = comprobantes.filter(
                Q(cuil_estudiante__icontains=buscar) | Q(cuil_responsable__icontains=buscar)
            )

        # 📅 Filtro de fechas
        if fecha_desde:
            comprobantes = comprobantes.filter(marca_temporal__gte=fecha_desde)
        if fecha_hasta:
            comprobantes = comprobantes.filter(marca_temporal__lte=fecha_hasta)

        # 📅 Períodos rápidos
        hoy = datetime.now().date()
        if periodo == "hoy":
            comprobantes = comprobantes.filter(marca_temporal__startswith=hoy)
        elif periodo == "semana":
            inicio = hoy - timedelta(days=hoy.weekday())
            comprobantes = comprobantes.filter(marca_temporal__gte=inicio)
        elif periodo == "mes":
            comprobantes = comprobantes.filter(marca_temporal__startswith=hoy.strftime("%Y-%m"))

        # ⚙️ Estado
        if estado:
            comprobantes = comprobantes.filter(estado=estado)

    return render(request, 'comprobantes/lista_comprobantes.html', {
        'comprobantes': comprobantes,
    })

@require_POST
def cambiar_estado_comprobante(request):
    from apps.comprobantes.models import ComprobantePago

    comp_id = request.POST.get('id')
    nuevo_estado = request.POST.get('estado')

    try:
        comp = ComprobantePago.objects.get(pk=comp_id)
        comp.estado = nuevo_estado
        comp.save()
        return JsonResponse({'success': True, 'nuevo_estado': nuevo_estado})
    except ComprobantePago.DoesNotExist:
        raise Http404("Comprobante no encontrado")