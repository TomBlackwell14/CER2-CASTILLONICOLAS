
from django.shortcuts import render

def inicio(request):
    return render(request, 'core/inicio.html')

def informacion(request):
    return render(request, 'core/informacion.html')

