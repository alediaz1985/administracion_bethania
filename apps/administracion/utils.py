# apps/administracion/utils.py
from .models import Cuota

def actualizar_cuotas_vencidas():
    """
    Recorre todas las cuotas pendientes y aplica interés si ya vencieron.
    """
    cuotas = Cuota.objects.filter(estado='Pendiente')
    for cuota in cuotas:
        cuota.aplicar_interes()
