from django.shortcuts import render

def cuotas_list(request):
    return render(request, 'cuotas/cuotas_list.html')
