from django.shortcuts import render
from apps.administracion_alumnos.models import Estudiante
from apps.cuotas.models import Cuota
from apps.documentos.models import Documento
from django.db.models import Sum, Count

def panel(request):
    total_estudiantes = Estudiante.objects.count()
    total_documentos = Documento.objects.count()
    total_cuotas_pagadas = Cuota.objects.filter(pagado=True).aggregate(total=Sum('total_a_pagar'))['total'] or 0
    cuotas_pendientes = Cuota.objects.filter(pagado=False).count()

    # Agrupar estudiantes por nivel
    nivel_data = Estudiante.objects.values('nivel_estudiante').annotate(total=Count('id'))
    labels = [item['nivel_estudiante'] for item in nivel_data]
    cantidades = [item['total'] for item in nivel_data]

    context = {
        'total_estudiantes': total_estudiantes,
        'total_documentos': total_documentos,
        'total_cuotas_pagadas': total_cuotas_pagadas,
        'cuotas_pendientes': cuotas_pendientes,
        'niveles_labels': labels,
        'niveles_data': cantidades,
    }

    return render(request, 'dashboard/panel.html', context)
