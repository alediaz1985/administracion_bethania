# apps/cuotas/services.py
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from calendar import monthrange

from django.apps import apps
from django.db import transaction


def _dec(val) -> Decimal:
    return (val if isinstance(val, Decimal) else Decimal(str(val))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _get_model(model_name: str):
    return apps.get_model("cuotas", model_name)


def _get_models():
    """
    Resuelve los modelos de forma perezosa para evitar import cycles y soportar renombres.
    Retorna:
      Inscripcion, Cuota, CicloLectivo, VencimientoMensual, TarifaModel
    Donde TarifaModel puede ser PlanArancelario o Tarifa, el que exista.
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
            "Creá uno de esos modelos (con campos: ciclo, nivel, monto_inscripcion, monto_cuota, "
            "vigente_desde, vigente_hasta opcional)."
        )

    return Inscripcion, Cuota, CicloLectivo, VencimientoMensual, TarifaModel


def _plan_vigente_para(fecha: date, ciclo, nivel, TarifaModel):
    """
    Busca el plan/tarifa vigente para una fecha dada.
    Requiere campos: vigente_desde (date) y vigente_hasta (date|null).
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

    # fallback: buscar manualmente alguno que aplique
    for p in TarifaModel.objects.filter(ciclo=ciclo, nivel=nivel).order_by("-vigente_desde"):
        hasta = getattr(p, "vigente_hasta", None)
        if p.vigente_desde <= fecha and (not hasta or fecha <= hasta):
            return p
    return None


def _monto_base_cuota_para(inscripcion, mes: int, TarifaModel) -> Decimal:
    """Monto base de la cuota para el mes, aplicando override del curso si existe."""
    dia = date(inscripcion.ciclo.anio, mes, 1)
    plan = _plan_vigente_para(dia, ciclo=inscripcion.ciclo, nivel=inscripcion.nivel, TarifaModel=TarifaModel)
    if not plan:
        raise ValueError("No existe plan/tarifa vigente para ese Ciclo/Nivel en ese mes.")

    # override por curso si está seteado
    override = getattr(inscripcion.curso, "override_monto_cuota", None)
    if override is not None:
        return _dec(override)

    return _dec(plan.monto_cuota)


def _fecha_vencimiento(ciclo, mes: int, VencimientoMensual) -> date:
    cfg = VencimientoMensual.objects.filter(ciclo=ciclo, mes=mes).first()
    if cfg:
        last_day = monthrange(ciclo.anio, mes)[1]
        dia = min(cfg.dia_vencimiento, last_day)
        return date(ciclo.anio, mes, dia)
    # Fallback: día 10
    last_day = monthrange(ciclo.anio, mes)[1]
    dia = min(10, last_day)
    return date(ciclo.anio, mes, dia)


@transaction.atomic
def generar_cuotas_para_inscripcion(inscripcion, meses: list[int]):
    """
    Crea (si no existen) y recalcula cuotas para los meses dados.
    - Si la cuota ya existe y NO está pagada, refresca importe_base y vencimiento y recomputa importe_final.
    - Si está pagada, no se toca.
    """
    Inscripcion, Cuota, CicloLectivo, VencimientoMensual, TarifaModel = _get_models()
    result = []

    for mes in meses:
        importe_base = _monto_base_cuota_para(inscripcion, mes, TarifaModel)
        venc = _fecha_vencimiento(inscripcion.ciclo, mes, VencimientoMensual)

        cuota, created = Cuota.objects.get_or_create(
            inscripcion=inscripcion,
            mes=mes,
            defaults={
                "importe_base": importe_base,
                "descuento": _dec("0.00"),
                "recargo": _dec("0.00"),
                "importe_final": importe_base,
                "fecha_vencimiento": venc,
            }
        )

        if not created and not cuota.pagado:
            cuota.importe_base = importe_base
            cuota.fecha_vencimiento = venc
            base = _dec(cuota.importe_base) - _dec(cuota.descuento)
            if base < 0:
                base = _dec("0.00")
            cuota.importe_final = base

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
    for ins in Inscripcion.objects.select_related("ciclo", "nivel", "curso").filter(ciclo=ciclo):
        total += len(generar_cuotas_para_inscripcion(ins, meses))
    return total
