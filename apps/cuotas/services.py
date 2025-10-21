# apps/cuotas/services.py
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from calendar import monthrange

from django.apps import apps
from django.db import transaction


# ==========================
# Helpers numéricos básicos
# ==========================
def _dec(val) -> Decimal:
    """
    Convierte a Decimal(2) con HALF_UP (estilo contable).
    Acepta int, float, str, Decimal.
    """
    return (val if isinstance(val, Decimal) else Decimal(str(val))).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


# ==========================
# Resolución perezosa de modelos (evita import cycles)
# ==========================
def _get_model(model_name: str):
    return apps.get_model("cuotas", model_name)


def _get_models():
    """
    Retorna:
      Inscripcion, Cuota, CicloLectivo, VencimientoMensual, TarifaModel
    Donde TarifaModel puede ser PlanArancelario o Tarifa (el que exista).
    """
    Inscripcion = _get_model("Inscripcion")
    Cuota = _get_model("Cuota")
    CicloLectivo = _get_model("CicloLectivo")
    VencimientoMensual = _get_model("VencimientoMensual")

    TarifaModel = None
    for name in ("PlanArancelario", "Tarifa"):
        try:
            TarifaModel = _get_model(name)
            if TarifaModel is not None:
                break
        except Exception:
            pass

    if TarifaModel is None:
        raise ImportError(
            "No se encontró ni 'PlanArancelario' ni 'Tarifa' en apps.cuotas.models. "
            "Creá uno de esos modelos con campos: ciclo, nivel, monto_inscripcion, monto_cuota, "
            "vigente_desde (date) y opcional vigente_hasta (date)."
        )

    return Inscripcion, Cuota, CicloLectivo, VencimientoMensual, TarifaModel


# ==========================
# Lógica de planes / montos base
# ==========================
def _plan_vigente_para(fecha: date, ciclo, nivel, TarifaModel):
    """
    Busca el plan/tarifa vigente para una fecha dada (fecha ∈ [vigente_desde, vigente_hasta?]).
    """
    plan = (
        TarifaModel.objects
        .filter(ciclo=ciclo, nivel=nivel, vigente_desde__lte=fecha)
        .order_by("-vigente_desde")
        .first()
    )
    if plan and getattr(plan, "vigente_hasta", None):
        if fecha > plan.vigente_hasta:
            plan = None

    if plan:
        return plan

    # Fallback más laxo por si faltan índices/consultas complejas
    for p in TarifaModel.objects.filter(ciclo=ciclo, nivel=nivel).order_by("-vigente_desde"):
        hasta = getattr(p, "vigente_hasta", None)
        if p.vigente_desde <= fecha and (not hasta or fecha <= hasta):
            return p
    return None


def _monto_base_cuota_para(inscripcion, mes: int, TarifaModel) -> Decimal:
    """
    Monto base de la cuota para el mes, aplicando override del curso si existe.
    """
    dia = date(inscripcion.ciclo.anio, mes, 1)
    plan = _plan_vigente_para(dia, ciclo=inscripcion.ciclo, nivel=inscripcion.nivel, TarifaModel=TarifaModel)
    if not plan:
        raise ValueError("No existe plan/tarifa vigente para ese Ciclo/Nivel en ese mes.")

    # override por curso si está seteado (e.g., curso.override_monto_cuota)
    override = getattr(inscripcion.curso, "override_monto_cuota", None)
    if override is not None:
        return _dec(override)

    return _dec(plan.monto_cuota)


# ==========================
# Vencimiento (fecha de corte sin recargo)
# ==========================
def _fecha_corte_sin_recargo(ciclo, mes: int, VencimientoMensual) -> date:
    """
    Devuelve la fecha límite real (1..último día del mes) para pagar SIN recargo.
    Usa VencimientoMensual.dia_ultimo_sin_recargo (clamp al fin de mes).
    Si no hay configuración, usa día 10 por defecto.
    """
    cfg = VencimientoMensual.objects.filter(ciclo=ciclo, mes=mes).first()
    last_day = monthrange(ciclo.anio, mes)[1]
    if cfg:
        dia = min(cfg.dia_ultimo_sin_recargo, last_day)
        return date(ciclo.anio, mes, dia)
    # Fallback: día 10
    dia = min(10, last_day)
    return date(ciclo.anio, mes, dia)


# ==========================
# Cálculo de recargo y total
# ==========================
def _porcentaje_recargo_para_fecha(ciclo, mes: int, fecha_pago: date, VencimientoMensual) -> Decimal:
    """
    Devuelve el porcentaje de recargo aplicable según la fecha de pago.
    0% si pago ≤ fecha_corte; recargo_porcentaje si pago > fecha_corte.
    """
    cfg = VencimientoMensual.objects.filter(ciclo=ciclo, mes=mes).first()
    if not cfg:
        # Si no hay cfg, por defecto NO recargo (o podrías setear 10% fijo si querés)
        return _dec("0.00")

    fecha_corte = _fecha_corte_sin_recargo(ciclo, mes, VencimientoMensual)
    return _dec(cfg.recargo_porcentaje) if fecha_pago > fecha_corte else _dec("0.00")


def calcular_importe_con_recargo(*, ciclo, mes: int, importe_base: Decimal, fecha_pago: date) -> dict:
    """
    Calcula recargo y total para la cuota del 'mes' de un 'ciclo' dado.
    Reglas:
      - Del 1 al 'dia_ultimo_sin_recargo' (clamp): 0% recargo
      - Desde el día siguiente: 'recargo_porcentaje' (configurable por mes/ciclo)
    """
    _, _, _, VencimientoMensual, _ = _get_models()

    base = _dec(importe_base)
    fecha_corte = _fecha_corte_sin_recargo(ciclo, mes, VencimientoMensual)
    porcentaje = _porcentaje_recargo_para_fecha(ciclo, mes, fecha_pago, VencimientoMensual)

    recargo = (base * porcentaje / _dec("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = (base + recargo).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "porcentaje": porcentaje,        # Decimal (ej. 10.00)
        "fecha_corte": fecha_corte,      # date
        "aplica_recargo": porcentaje > 0,
        "recargo": recargo,              # Decimal(2)
        "total": total,                  # Decimal(2)
    }


# ==========================
# Generación / actualización de cuotas
# ==========================
@transaction.atomic
def generar_cuotas_para_inscripcion(inscripcion, meses: list[int]):
    """
    Crea (si no existen) y recalcula cuotas para los meses dados.
    - Si la cuota ya existe y NO está pagada, refresca importe_base y fecha_corte y recomputa importe_final (sin recargo).
    - Si está pagada, no se toca.
    """
    Inscripcion, Cuota, CicloLectivo, VencimientoMensual, TarifaModel = _get_models()
    result = []

    for mes in meses:
        # 1) Monto base según plan vigente (o override del curso)
        importe_base = _monto_base_cuota_para(inscripcion, mes, TarifaModel)

        # 2) Fecha de corte (sin recargo) que guardamos como "fecha_vencimiento" para UI/reportes
        fecha_corte = _fecha_corte_sin_recargo(inscripcion.ciclo, mes, VencimientoMensual)

        cuota, created = Cuota.objects.get_or_create(
            inscripcion=inscripcion,
            mes=mes,
            defaults={
                "importe_base": importe_base,
                "descuento": _dec("0.00"),
                "recargo": _dec("0.00"),
                "importe_final": importe_base,   # base - desc (recargo se evalúa al cobrar)
                "fecha_vencimiento": fecha_corte,
            }
        )

        if not created and not getattr(cuota, "pagado", False):
            # Refrescamos datos variables
            cuota.importe_base = importe_base
            cuota.fecha_vencimiento = fecha_corte

            # Recalcular importe_final sin recargo (aplica al momento de cobrar)
            base_neta = _dec(cuota.importe_base) - _dec(getattr(cuota, "descuento", _dec("0.00")))
            if base_neta < 0:
                base_neta = _dec("0.00")
            cuota.importe_final = base_neta

        cuota.save()
        result.append(cuota)

    return result


@transaction.atomic
def generar_cuotas_masivo(ciclo, meses: list[int]) -> int:
    """
    Genera/actualiza cuotas para TODAS las inscripciones de un ciclo.
    Devuelve cantidad de cuotas afectadas.
    """
    Inscripcion, Cuota, CicloLectivo, VencimientoMensual, TarifaModel = _get_models()
    total = 0
    qs = (
        Inscripcion.objects
        .select_related("ciclo", "nivel", "curso")
        .filter(ciclo=ciclo)
    )
    for ins in qs:
        total += len(generar_cuotas_para_inscripcion(ins, meses))
    return total


# ==========================
# Cobro: aplicar regla a una cuota puntual
# ==========================
@transaction.atomic
def aplicar_cobro_a_cuota(cuota_id: int, fecha_pago: date | None = None) -> dict:
    """
    Aplica la regla de vencimiento/recargo a la cuota indicada y la marca como pagada.
    - Recalcula recargo en ese momento en base a la fecha_pago (default: hoy).
    - Actualiza: recargo, importe_final (= base_neta + recargo), fecha_pago y pagado=True.
    - Devuelve dict con el detalle del cálculo.
    """
    _, Cuota, _, _, _ = _get_models()
    cuota = Cuota.objects.select_related("inscripcion", "inscripcion__ciclo").get(id=cuota_id)

    fecha_pago = fecha_pago or date.today()
    base_neta = _dec(cuota.importe_base) - _dec(getattr(cuota, "descuento", _dec("0.00")))
    if base_neta < 0:
        base_neta = _dec("0.00")

    datos = calcular_importe_con_recargo(
        ciclo=cuota.inscripcion.ciclo,
        mes=cuota.mes,
        importe_base=base_neta,
        fecha_pago=fecha_pago,
    )

    # Persistimos en la cuota
    cuota.recargo = datos["recargo"]
    cuota.importe_final = datos["total"]
    setattr(cuota, "fecha_pago", fecha_pago)
    setattr(cuota, "pagado", True)
    cuota.save()

    # Devolvemos info útil para UI/mensajes
    return {
        "cuota_id": cuota.id,
        "mes": cuota.mes,
        "fecha_corte": datos["fecha_corte"],
        "porcentaje": datos["porcentaje"],
        "aplica_recargo": datos["aplica_recargo"],
        "recargo": datos["recargo"],
        "total": datos["total"],
        "fecha_pago": fecha_pago,
    }
